#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <wayland-client.h>
#include "xdg-shell-client.h"

/* EXPERIMENTAL CONTRACT: every popup owns distinct XDG objects. B's actual
 * parent is A's xdg_surface; logs name object IDs as well as colors. */
struct surface {
    const char *name;
    struct wl_surface *wl;
    struct xdg_surface *xdg;
    struct xdg_popup *popup;
    bool configured, mapped, done;
    int width, height, anchor_x, anchor_y;
    uint32_t color;
};
static struct wl_display *display;
static struct wl_compositor *compositor;
static struct wl_shm *shm;
static struct xdg_wm_base *wm;
static struct wl_seat *seat;
static struct wl_pointer *pointer;
static struct xdg_toplevel *top_role;
static struct surface top = {.name="TOPLEVEL", .width=420, .height=320, .color=0x002344cc};
static struct surface a = {.name="POPUP_A", .width=300, .height=170, .color=0x00e0c020};
static struct surface b = {.name="POPUP_B", .width=300, .height=130, .color=0x0020d0a0};
static volatile sig_atomic_t running = 1;
static struct surface *entered;

static void draw(struct surface *s) {
    size_t bytes = (size_t)s->width * (size_t)s->height * 4;
    char path[] = "/tmp/mosaic-nested-buffer-XXXXXX";
    int fd = mkstemp(path);
    if (fd < 0 || ftruncate(fd, (off_t)bytes) < 0) { perror("buffer"); exit(1); }
    unlink(path);
    uint32_t *pixels = mmap(NULL, bytes, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (pixels == MAP_FAILED) { perror("mmap"); exit(1); }
    for (size_t i=0; i<bytes/4; ++i) pixels[i] = s->color;
    struct wl_shm_pool *pool = wl_shm_create_pool(shm, fd, (int)bytes);
    struct wl_buffer *buffer = wl_shm_pool_create_buffer(pool, 0, s->width, s->height,
        s->width*4, WL_SHM_FORMAT_XRGB8888);
    wl_surface_attach(s->wl, buffer, 0, 0);
    wl_surface_damage_buffer(s->wl, 0, 0, s->width, s->height);
    wl_surface_commit(s->wl);
    wl_buffer_destroy(buffer);
    wl_shm_pool_destroy(pool);
    munmap(pixels, bytes);
    close(fd);
    s->mapped = true;
    fprintf(stderr, "%s MAP wl=%u xdg=%u\n", s->name,
        wl_proxy_get_id((struct wl_proxy *)s->wl), wl_proxy_get_id((struct wl_proxy *)s->xdg));
}
static void on_ping(void *data, struct xdg_wm_base *base, uint32_t serial) {
    xdg_wm_base_pong(base, serial);
}
static const struct xdg_wm_base_listener wm_listener = {.ping=on_ping};
static void on_xdg_configure(void *data, struct xdg_surface *xdg, uint32_t serial) {
    struct surface *s=data;
    fprintf(stderr, "%s XDG_CONFIGURE serial=%u ack\n", s->name, serial);
    xdg_surface_ack_configure(xdg, serial);
    s->configured=true;
    if (!s->mapped && !s->done) draw(s);
}
static const struct xdg_surface_listener xdg_listener = {.configure=on_xdg_configure};
static void on_top_configure(void *data, struct xdg_toplevel *role, int32_t w,
        int32_t h, struct wl_array *states) {
    fprintf(stderr, "TOPLEVEL ROLE_CONFIGURE w=%d h=%d\n", w,h);
}
static void on_top_close(void *data, struct xdg_toplevel *role) {
    fprintf(stderr, "TOPLEVEL CLOSE_REQUEST\n"); running=0;
}
static const struct xdg_toplevel_listener top_listener = {
    .configure=on_top_configure, .close=on_top_close,
};
static void on_popup_configure(void *data, struct xdg_popup *role, int32_t x,
        int32_t y, int32_t w, int32_t h) {
    struct surface *s=data;
    fprintf(stderr, "%s ROLE_CONFIGURE x=%d y=%d w=%d h=%d\n",s->name,x,y,w,h);
}
static void on_popup_done(void *data, struct xdg_popup *role) {
    struct surface *s=data;
    s->done=true;
    s->mapped=false;
    fprintf(stderr, "%s POPUP_DONE role=%u\n",s->name,wl_proxy_get_id((struct wl_proxy *)role));
}
static const struct xdg_popup_listener popup_listener = {
    .configure=on_popup_configure, .popup_done=on_popup_done,
};
/* WHY: XDG requires child-first destruction even if the compositor sends
 * dismissals for multiple levels in one dispatch batch. */
static void destroy_popup(struct surface *s) {
    if (!s->popup) return;
    fprintf(stderr,"%s DESTROY role=%u xdg=%u wl=%u\n",s->name,
        wl_proxy_get_id((struct wl_proxy *)s->popup),
        wl_proxy_get_id((struct wl_proxy *)s->xdg),
        wl_proxy_get_id((struct wl_proxy *)s->wl));
    xdg_popup_destroy(s->popup);
    xdg_surface_destroy(s->xdg);
    wl_surface_destroy(s->wl);
    s->popup=NULL; s->xdg=NULL; s->wl=NULL; s->mapped=false;
    if (entered==s) entered=NULL;
}
static void collect_dismissals(void) {
    if (b.done) destroy_popup(&b);
    if (a.done) {
        destroy_popup(&b);
        destroy_popup(&a);
    }
}
static void open_popup(struct surface *s, struct surface *parent, uint32_t serial) {
    if (s->popup || !parent->mapped || !serial) return;
    s->wl=wl_compositor_create_surface(compositor);
    s->xdg=xdg_wm_base_get_xdg_surface(wm,s->wl);
    xdg_surface_add_listener(s->xdg,&xdg_listener,s);
    struct xdg_positioner *pos=xdg_wm_base_create_positioner(wm);
    xdg_positioner_set_size(pos,s->width,s->height);
    xdg_positioner_set_anchor_rect(pos,s->anchor_x,s->anchor_y,1,1);
    xdg_positioner_set_anchor(pos,XDG_POSITIONER_ANCHOR_TOP_LEFT);
    xdg_positioner_set_gravity(pos,XDG_POSITIONER_GRAVITY_BOTTOM_RIGHT);
    s->popup=xdg_surface_get_popup(s->xdg,parent->xdg,pos);
    xdg_popup_add_listener(s->popup,&popup_listener,s);
    fprintf(stderr,"%s CREATE wl=%u xdg=%u role=%u parent=%s parent_xdg=%u\n",
        s->name,wl_proxy_get_id((struct wl_proxy *)s->wl),
        wl_proxy_get_id((struct wl_proxy *)s->xdg),
        wl_proxy_get_id((struct wl_proxy *)s->popup),parent->name,
        wl_proxy_get_id((struct wl_proxy *)parent->xdg));
    fprintf(stderr,"%s GRAB_REQUEST origin=wl_pointer.button target=%s serial=%u used=%u\n",
        s->name,parent->name,serial,serial);
    xdg_popup_grab(s->popup,seat,serial);
    wl_surface_commit(s->wl); /* Initial bufferless commit requests configure. */
    xdg_positioner_destroy(pos);
}
static struct surface *which(struct wl_surface *wl) {
    if (wl==top.wl) return &top;
    if (wl==a.wl && wl) return &a;
    if (wl==b.wl && wl) return &b;
    return NULL;
}
static void on_enter(void *data,struct wl_pointer *ptr,uint32_t serial,
        struct wl_surface *wl,wl_fixed_t x,wl_fixed_t y) {
    entered=which(wl);
    fprintf(stderr,"POINTER_ENTER target=%s wl=%u serial=%u x=%.2f y=%.2f\n",
        entered?entered->name:"OTHER",wl_proxy_get_id((struct wl_proxy *)wl),serial,
        wl_fixed_to_double(x),wl_fixed_to_double(y));
}
static void on_leave(void *data,struct wl_pointer *ptr,uint32_t serial,
        struct wl_surface *wl) {
    struct surface *s=which(wl);
    fprintf(stderr,"POINTER_LEAVE target=%s serial=%u\n",s?s->name:"OTHER",serial);
    if (entered==s) entered=NULL;
}
static void on_motion(void *data,struct wl_pointer *ptr,uint32_t time,
        wl_fixed_t x,wl_fixed_t y) {
    fprintf(stderr,"POINTER_MOTION target=%s x=%.2f y=%.2f\n",
        entered?entered->name:"OTHER",wl_fixed_to_double(x),wl_fixed_to_double(y));
}
static void on_button(void *data,struct wl_pointer *ptr,uint32_t serial,
        uint32_t time,uint32_t button,uint32_t state) {
    fprintf(stderr,"POINTER_BUTTON target=%s serial=%u button=%u state=%u\n",
        entered?entered->name:"OTHER",serial,button,state);
    if (state!=WL_POINTER_BUTTON_STATE_PRESSED || button!=272) return;
    if (entered==&top && !a.popup) open_popup(&a,&top,serial);
    else if (entered==&a && a.mapped && !b.popup) open_popup(&b,&a,serial);
}
static void on_axis(void *data,struct wl_pointer *ptr,uint32_t t,uint32_t axis,wl_fixed_t v) {}
static void on_frame(void *data,struct wl_pointer *ptr) {}
static const struct wl_pointer_listener pointer_listener={
    .enter=on_enter,.leave=on_leave,.motion=on_motion,.button=on_button,
    .axis=on_axis,.frame=on_frame,
};
static void on_caps(void *data,struct wl_seat *s,uint32_t caps) {
    if ((caps & WL_SEAT_CAPABILITY_POINTER) && !pointer) {
        pointer=wl_seat_get_pointer(s);
        wl_pointer_add_listener(pointer,&pointer_listener,NULL);
    }
}
static void on_seat_name(void *data,struct wl_seat *s,const char *name) {}
static const struct wl_seat_listener seat_listener={.capabilities=on_caps,.name=on_seat_name};
static void on_global(void *data,struct wl_registry *reg,uint32_t name,
        const char *interface,uint32_t version) {
    if (!strcmp(interface,wl_compositor_interface.name))
        compositor=wl_registry_bind(reg,name,&wl_compositor_interface,version<4?version:4);
    else if (!strcmp(interface,wl_shm_interface.name))
        shm=wl_registry_bind(reg,name,&wl_shm_interface,1);
    else if (!strcmp(interface,xdg_wm_base_interface.name))
        wm=wl_registry_bind(reg,name,&xdg_wm_base_interface,version<3?version:3);
    else if (!strcmp(interface,wl_seat_interface.name)) {
        seat=wl_registry_bind(reg,name,&wl_seat_interface,version<5?version:5);
        wl_seat_add_listener(seat,&seat_listener,NULL);
    }
}
static void on_removed(void *data,struct wl_registry *reg,uint32_t name) {}
static const struct wl_registry_listener registry_listener={.global=on_global,.global_remove=on_removed};
static void stop(int sig) { running=0; }
int main(int argc,char **argv) {
    signal(SIGTERM,stop);
    const char *placement=argc>1?argv[1]:"b_cross";
    /* EXPERIMENTAL: only placement changes; serial/grab/lifecycle stay historical.
     * Both 1x1 anchors lie inside their parent SHM window geometry. */
    if (!strcmp(placement,"static_cross")) {
        a.anchor_x=100; a.anchor_y=80; a.width=350;
        b.anchor_x=100; b.anchor_y=60; b.width=300;
    } else if (!strcmp(placement,"visible")) {
        a.anchor_x=50; a.anchor_y=80; a.width=250;
        b.anchor_x=20; b.anchor_y=60; b.width=170;
    } else if (!strcmp(placement,"both_cross")) {
        a.anchor_x=350; a.anchor_y=80; a.width=350;
        b.anchor_x=160; b.anchor_y=60; b.width=300;
    } else if (!strcmp(placement,"b_cross")) {
        a.anchor_x=200; a.anchor_y=80; a.width=300;
        b.anchor_x=220; b.anchor_y=60; b.width=300;
    } else { fprintf(stderr,"invalid placement\n"); return 2; }
    display=wl_display_connect(NULL);
    if (!display) { fprintf(stderr,"cannot connect Wayland\n"); return 1; }
    struct wl_registry *registry=wl_display_get_registry(display);
    wl_registry_add_listener(registry,&registry_listener,NULL);
    wl_display_roundtrip(display); wl_display_roundtrip(display);
    if (!compositor || !shm || !wm || !seat || !pointer) {
        fprintf(stderr,"missing Wayland globals/pointer\n"); return 1;
    }
    xdg_wm_base_add_listener(wm,&wm_listener,NULL);
    top.wl=wl_compositor_create_surface(compositor);
    top.xdg=xdg_wm_base_get_xdg_surface(wm,top.wl);
    xdg_surface_add_listener(top.xdg,&xdg_listener,&top);
    top_role=xdg_surface_get_toplevel(top.xdg);
    xdg_toplevel_add_listener(top_role,&top_listener,NULL);
    xdg_toplevel_set_title(top_role,"Mosaic Nested Grab Probe");
    xdg_toplevel_set_app_id(top_role,"org.mosaic.NestedGrabProbe");
    fprintf(stderr,"TOPLEVEL CREATE wl=%u xdg=%u role=%u placement=%s\n",
        wl_proxy_get_id((struct wl_proxy *)top.wl),
        wl_proxy_get_id((struct wl_proxy *)top.xdg),
        wl_proxy_get_id((struct wl_proxy *)top_role),placement);
    wl_surface_commit(top.wl);
    while (running) {
        wl_display_flush(display);
        struct pollfd fds[2]={{.fd=wl_display_get_fd(display),.events=POLLIN},
            {.fd=STDIN_FILENO,.events=POLLIN}};
        int ready=poll(fds,2,500);
        if (ready<0) { if (errno==EINTR) continue; perror("poll"); break; }
        if (fds[0].revents & (POLLIN|POLLERR|POLLHUP)) {
            if (wl_display_dispatch(display)<0) break;
            collect_dismissals();
        }
        if (fds[1].revents & POLLIN) {
            char cmd[64];
            if (fgets(cmd,sizeof(cmd),stdin)) {
                if (!strncmp(cmd,"close_b",7)) { destroy_popup(&b); fprintf(stderr,"COMMAND close_b DONE\n"); }
                else if (!strncmp(cmd,"close_owner",11)) { fprintf(stderr,"COMMAND close_owner\n"); running=0; }
            }
        }
    }
    destroy_popup(&b); destroy_popup(&a);
    fprintf(stderr,"TOPLEVEL DESTROY\n");
    xdg_toplevel_destroy(top_role); xdg_surface_destroy(top.xdg); wl_surface_destroy(top.wl);
    wl_display_flush(display);
    /* WHY/CONTRACT/INVARIANT: exit0 does not prove protocol error0. */
    fprintf(stderr,"EXIT error=%d\n",wl_display_get_error(display));
    wl_display_disconnect(display);
    return 0;
}
