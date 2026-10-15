#define _POSIX_C_SOURCE 200809L
#define WLR_USE_UNSTABLE
#define WLR_PRIVATE
#define WLR_INFO 1
#define wlr_log(level, ...) ((void)(level))
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <wayland-server-core.h>
#include <pixman.h>
#include <scenefx/types/wlr_scene.h>
#include <wlr/render/drm_syncobj.h>
// Adapters: no renderer/output/damage qualification. Actual native scene
// structs, addon set, signals and Pixman are used. Only tree paths exercised.
static unsigned updates, attempts, reservations, fail_reservation, fail_hits;
static void scene_node_update(struct wlr_scene_node *n, pixman_region32_t *damage) {
    (void)n; updates++; if(damage) pixman_region32_fini(damage);
}
static void scene_node_visibility(struct wlr_scene_node *n,pixman_region32_t *r) {(void)n;(void)r;}
static void scene_buffer_set_buffer(struct wlr_scene_buffer *n,struct wlr_buffer *b) {(void)n;(void)b;abort();}
static void scene_buffer_set_texture(struct wlr_scene_buffer *n,struct wlr_texture *t) {(void)n;(void)t;abort();}
void linked_node_destroy(struct linked_node *n) {(void)n;abort();}
static size_t sidecar_size;
static struct wlr_scene_tree *watched;
static int expected_children;
static void *injected_calloc(size_t count,size_t size) {
    attempts++;
    if (size==sidecar_size) {
        reservations++;
        assert(!watched || wl_list_length(&watched->children)==expected_children);
        if(reservations==fail_reservation){fail_hits++;return NULL;}
    }
    return calloc(count,size);
}
static void injected_free(void *p) {
    // Test adapter: assert admission parent state before freeing unpublished tree.
    assert(!watched || wl_list_length(&watched->children)==expected_children);
    free(p);
}
#define free injected_free
#define calloc injected_calloc
#include "scene.inc"
#undef calloc
#undef free
#include "geometry.inc"
static unsigned count_clips(void) {unsigned n=0;for(struct scene_tree_clip *it=scene_tree_clips;it;it=it->next)n++;return n;}
static unsigned inactive_count(void) {unsigned n=0;for(struct scene_tree_clip *it=scene_tree_clips;it;it=it->next)if(!it->active)n++;return n;}
#include "ime-support.inc"
#include "transaction-support.inc"
static struct wlr_scene *make_root(void) {
    struct wlr_scene *s=calloc(1,sizeof(*s));assert(s);scene_tree_init(&s->tree,NULL);
    wl_list_init(&s->outputs);wl_list_init(&s->linux_dmabuf_v1_destroy.link);
    wl_list_init(&s->gamma_control_manager_v1_destroy.link);wl_list_init(&s->gamma_control_manager_v1_set_gamma.link);return s;
}
static void __attribute__((unused)) geometry(void) {
    struct wlr_box a={INT_MIN,INT_MIN,1,1},b={800,0,800,600},r;
    assert(!probe_clip_box_intersection(&r,&a,&b));assert(r.width==0);
    a=(struct wlr_box){INT_MAX-2,0,2,10};b=a;assert(probe_clip_box_intersection(&a,&a,&b));assert(a.width==2);
    a=(struct wlr_box){INT_MIN,0,INT_MAX,20};b=(struct wlr_box){-10,1,20,10};assert(probe_clip_box_intersection(&b,&a,&b));assert(b.x==-10&&b.width==9);
    a=(struct wlr_box){INT_MAX,0,1,1};assert(!scene_clip_translate(&a,1,0,&a));assert(a.width==0);
    a=(struct wlr_box){1,2,3,4};assert(scene_clip_translate(&a,2,3,&a));assert(a.x==3&&a.y==5);
    assert(probe_camera_scroll(NAN)==0);assert(probe_camera_scroll(INFINITY)==0);assert(probe_camera_scroll(-INFINITY)==0);
    assert(probe_camera_scroll(1e300)==INT_MAX);assert(probe_camera_scroll(-1e300)==0);assert(probe_camera_scroll(42.9)==42);
}
static void token_write(const char *content, mode_t mode) {
    int fd=open(oom_diag.path,O_CREAT|O_EXCL|O_WRONLY,0600);assert(fd>=0);
    size_t n=strlen(content);assert(write(fd,content,n)==(ssize_t)n);
    assert(fchmod(fd,mode)==0);assert(close(fd)==0);
}
static struct wlr_scene_tree *primary(struct wlr_scene_tree *p,const char *r) {
    return smx_oom_popup_tree_create(p,r,(const void *)0x1234,(const void *)0x5678);
}
int main(int argc,char **argv) {
    assert(prctl(PR_SET_DUMPABLE,0,0,0,0)==0);
    assert(prctl(PR_GET_DUMPABLE,0,0,0,0)==0);
    assert(argc==2);sidecar_size=sizeof(struct scene_tree_clip);
    struct wlr_scene *s=make_root();struct wlr_scene_tree *root=&s->tree;
    char valid[80];snprintf(valid,sizeof(valid),"SMXOOM1 %s %s\n",oom_diag.nonce,oom_diag.role);
    bool inject=!strcmp(argv[1],"root")||!strcmp(argv[1],"nested");
    struct wlr_scene_tree *a=NULL,*b=NULL;
    if(!strcmp(argv[1],"nested")) {
        a=primary(root,"root_popup");assert(a);assert(oom_diag.successes==1);
        assert(count_clips()==1); // rootA exists before the runner arms.
    }
    if(strcmp(argv[1],"unarmed") && strcmp(argv[1],"invalidenv")) {
        if(!strcmp(argv[1],"malformed")) token_write("bad token\n",0600);
        else if(!strcmp(argv[1],"nonce")) token_write("SMXOOM1 00000000000000000000000000000000 root_popup\n",0600);
        else if(!strcmp(argv[1],"mode")) token_write(valid,0644);
        else if(!strcmp(argv[1],"symlink")) {assert(symlink("/dev/null",oom_diag.path)==0);}
        else token_write(valid,0600);
    }
    // Ordinary/native factories never acquire diagnostic authority, even armed.
    unsigned before=count_clips();b=wlr_scene_tree_create(root);assert(b);
    assert(!oom_diag.failures);wlr_scene_node_destroy(&b->node);assert(count_clips()==before);
    const char *role=!strcmp(argv[1],"nested")?"nested_popup":
        !strcmp(argv[1],"wrongrole")?"nested_popup":"root_popup";
    struct wlr_scene_tree *parent=a?a:root;
    unsigned children=(unsigned)wl_list_length(&parent->children), clips=count_clips();
    unsigned listener_count=(unsigned)wl_list_length(&parent->node.events.destroy.listener_list);
    watched=parent;expected_children=(int)children;
    b=primary(parent,role);watched=NULL;
    if(inject) {
        assert(!b);assert(errno==ENOMEM);assert(oom_diag.failures==1&&oom_diag.matched==1);
        assert((unsigned)wl_list_length(&parent->children)==children);
        assert(count_clips()==clips);
        assert((unsigned)wl_list_length(&parent->node.events.destroy.listener_list)==listener_count);
        assert(!oom_diag.scoped&&!oom_diag.call_role&&!oom_diag.xdg&&!oom_diag.xdg_parent);
        // The same valid token is still present: it must never trigger twice.
        b=primary(parent,role);assert(b&&oom_diag.failures==1);
    } else {assert(b);assert(!oom_diag.failures&&!oom_diag.consumed);}
    wlr_scene_node_destroy(&root->node);assert(!count_clips());
    printf("PASS case=%s failures=%u matched=%u successes=%u final_reservations=0\n",argv[1],oom_diag.failures,oom_diag.matched,oom_diag.successes);
    return 0;
}
