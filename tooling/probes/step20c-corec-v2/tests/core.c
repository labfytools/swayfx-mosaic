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
#define calloc injected_calloc
#include "scene.inc"
#undef calloc
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
static void geometry(void) {
    struct wlr_box a={INT_MIN,INT_MIN,1,1},b={800,0,800,600},r;
    assert(!probe_clip_box_intersection(&r,&a,&b));assert(r.width==0);
    a=(struct wlr_box){INT_MAX-2,0,2,10};b=a;assert(probe_clip_box_intersection(&a,&a,&b));assert(a.width==2);
    a=(struct wlr_box){INT_MIN,0,INT_MAX,20};b=(struct wlr_box){-10,1,20,10};assert(probe_clip_box_intersection(&b,&a,&b));assert(b.x==-10&&b.width==9);
    a=(struct wlr_box){INT_MAX,0,1,1};assert(!scene_clip_translate(&a,1,0,&a));assert(a.width==0);
    a=(struct wlr_box){1,2,3,4};assert(scene_clip_translate(&a,2,3,&a));assert(a.x==3&&a.y==5);
    assert(probe_camera_scroll(NAN)==0);assert(probe_camera_scroll(INFINITY)==0);assert(probe_camera_scroll(-INFINITY)==0);
    assert(probe_camera_scroll(1e300)==INT_MAX);assert(probe_camera_scroll(-1e300)==0);assert(probe_camera_scroll(42.9)==42);
}
int main(int argc,char **argv) {
    // Linux piped core handlers may ignore RLIMIT_CORE: disable dumps in
    // the child itself before any expected assertion or sanitizer failure.
    assert(prctl(PR_SET_DUMPABLE,0,0,0,0)==0);
    assert(prctl(PR_GET_DUMPABLE,0,0,0,0)==0);
    sidecar_size=sizeof(struct scene_tree_clip);geometry();
    struct wlr_scene *s=make_root();struct wlr_scene_tree *root=&s->tree;
    if(argc>1 && !strcmp(argv[1],"root")) {wlr_scene_tree_set_clip(root,NULL);wlr_scene_node_destroy(&root->node);return 0;}
    if(argc>1 && !strcmp(argv[1],"second")) {
        watched=root;expected_children=0;fail_reservation=2;
        struct wlr_scene_tree *first=wlr_scene_tree_create(root);assert(first);
        expected_children=1;assert(!wlr_scene_tree_create(root));assert(reservations==2);
        assert(wl_list_length(&root->children)==1&&count_clips()==1);
        assert(wl_list_empty(&root->node.events.destroy.listener_list));
        wlr_scene_node_destroy(&root->node);assert(!count_clips());puts("PASS targeted_second_reservation");return 0;
    }
    watched=root;expected_children=0;fail_reservation=1;
    assert(!wlr_scene_tree_create(root));assert(wl_list_empty(&root->children));assert(!count_clips());
    assert(wl_list_empty(&root->node.events.destroy.listener_list));
    fail_reservation=0;
    struct wlr_scene_tree *a=wlr_scene_tree_create(root);assert(a);assert(count_clips()==1);assert(inactive_count()==1);unsigned inactive_initial=inactive_count();
    assert(wl_list_length(&a->node.events.destroy.listener_list)==1);
    assert(!wlr_scene_tree_get_clip(a,&(struct wlr_box){0}));assert(scene_node_point_inside_clip(&a->node,100,100));
    unsigned prior=attempts;struct wlr_box box={0,0,10,10},zero={0},out;
    wlr_scene_tree_set_clip(a,NULL);wlr_scene_tree_set_clip(a,&box);assert(wlr_scene_tree_get_clip(a,&out));
    unsigned u=updates;wlr_scene_tree_set_clip(a,&box);assert(updates==u);
    assert(scene_node_point_inside_clip(&a->node,1,1));assert(!scene_node_point_inside_clip(&a->node,10,1));
    struct wlr_scene_rect rect={.accepts_input=true};scene_node_init(&rect.node,WLR_SCENE_NODE_RECT,a);
    struct node_at_data hit={.lx=1,.ly=1};assert(scene_node_at_iterator(&rect.node,0,0,&hit));
    wlr_scene_tree_set_clip(a,&zero);assert(!scene_node_point_inside_clip(&a->node,0,0));
    hit=(struct node_at_data){.lx=1,.ly=1};assert(!scene_node_at_iterator(&rect.node,0,0,&hit)&&!hit.node);
    wl_list_remove(&rect.node.link);pixman_region32_fini(&rect.node.visible);
    pixman_region32_t region;pixman_region32_init_rect(&region,0,0,100,100);scene_node_intersect_clip(&a->node,&region);assert(pixman_region32_empty(&region));pixman_region32_fini(&region);
    wlr_scene_tree_set_clip(a,NULL);assert(count_clips()==1);assert(!wlr_scene_tree_get_clip(a,&out));
    wlr_scene_tree_set_clip(a,&box);assert(attempts==prior);
    expected_children=1;fail_reservation=reservations+1;assert(!wlr_scene_tree_create(root));assert(wl_list_length(&root->children)==1);assert(count_clips()==1);
    fail_reservation=0;struct wlr_scene_tree *b=wlr_scene_tree_create(root);assert(b);
    watched=NULL;struct wlr_scene_tree *c=wlr_scene_tree_create(a);assert(c);
    unsigned inactive_three=inactive_count(),reserved_three=count_clips();assert(inactive_three==2&&reserved_three==3);
    assert(!scene_node_point_inside_clip(&c->node,50,50));
    wlr_scene_node_reparent(&c->node,b);assert(scene_node_point_inside_clip(&c->node,50,50));
    wlr_scene_node_reparent(&c->node,a);assert(!scene_node_point_inside_clip(&c->node,50,50));
    a->node.x=INT_MAX;c->node.x=100;int x,y;assert(!wlr_scene_node_coords(&c->node,&x,&y));a->node.x=c->node.x=0;
    wlr_scene_node_destroy(&a->node);assert(count_clips()==1); // parent before child
    c=wlr_scene_tree_create(b);wlr_scene_node_destroy(&c->node);wlr_scene_node_destroy(&b->node);assert(!count_clips());
    for(int i=0;i<100;i++){a=wlr_scene_tree_create(root);assert(!wlr_scene_tree_get_clip(a,&out));wlr_scene_node_destroy(&a->node);} // allocator address reuse
    assert(!count_clips());ime_tests(root);transaction_tests(root);wlr_scene_node_destroy(&root->node);
    printf("PASS native_struct_tree=%zu sidecar=%zu allocation_attempts=%u reservation_attempts=%u injected_failures=%u inactive_initial=%u inactive_three_trees=%u reserved_three_trees=%u final_reservations=%u dumpable=0 lookup=linear allocator_overhead=NOT_MEASURED damage=ADAPTER_ONLY\n",sizeof(struct wlr_scene_tree),sidecar_size,attempts,reservations,fail_hits,inactive_initial,inactive_three,reserved_three,count_clips());
    return 0;
}
