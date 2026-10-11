#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <fcntl.h>
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

static struct wl_display *display;
static struct wl_compositor *compositor;
static struct wl_shm *shm;
static struct xdg_wm_base *wm;
static struct wl_seat *seat;
static struct wl_pointer *pointer;
static struct wl_surface *top_surface, *popup_surface;
static struct xdg_surface *top_xdg, *popup_xdg;
static struct xdg_toplevel *top_role;
static struct xdg_popup *popup_role;
static bool top_drawn, popup_drawn;
static int popup_width = 500, popup_anchor_x = 350;
static volatile sig_atomic_t running = 1;

static void draw(struct wl_surface *surface, int width, int height, uint32_t color) {
    int size = width * height * 4;
    char path[] = "/tmp/mosaic-grab-buffer-XXXXXX";
    int fd = mkstemp(path);
    if (fd < 0 || ftruncate(fd, size) < 0) { perror("buffer"); exit(1); }
    unlink(path);
    uint32_t *pixels = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (pixels == MAP_FAILED) { perror("mmap"); exit(1); }
    for (int i = 0; i < width * height; ++i) pixels[i] = color;
    struct wl_shm_pool *pool = wl_shm_create_pool(shm, fd, size);
    struct wl_buffer *buffer = wl_shm_pool_create_buffer(pool, 0, width, height,
        width * 4, WL_SHM_FORMAT_XRGB8888);
    wl_surface_attach(surface, buffer, 0, 0);
    wl_surface_damage_buffer(surface, 0, 0, width, height);
    wl_surface_commit(surface);
    wl_buffer_destroy(buffer);
    wl_shm_pool_destroy(pool);
    munmap(pixels, size);
    close(fd);
}
static void wm_ping(void *data, struct xdg_wm_base *base, uint32_t serial) {
    xdg_wm_base_pong(base, serial);
}
static const struct xdg_wm_base_listener wm_listener = {.ping = wm_ping};
static void xdg_configure(void *data, struct xdg_surface *surface, uint32_t serial) {
    xdg_surface_ack_configure(surface, serial);
    if (surface == top_xdg && !top_drawn) {
        top_drawn = true;
        fprintf(stderr, "TOP_CONFIGURE serial=%u map=1\n", serial);
        draw(top_surface, 420, 320, 0x002344cc);
    } else if (surface == popup_xdg && !popup_drawn) {
        popup_drawn = true;
        fprintf(stderr, "POPUP_XDG_CONFIGURE serial=%u map=1\n", serial);
        draw(popup_surface, popup_width, 190, 0x00e0c020);
    }
}
static const struct xdg_surface_listener surface_listener = {.configure = xdg_configure};
static void top_configure(void *data, struct xdg_toplevel *top, int32_t width,
        int32_t height, struct wl_array *states) {
    fprintf(stderr, "TOP_ROLE_CONFIGURE width=%d height=%d\n", width, height);
}
static void top_close(void *data, struct xdg_toplevel *top) {
    fprintf(stderr, "TOP_CLOSE\n"); running = 0;
}
static const struct xdg_toplevel_listener top_listener = {
    .configure = top_configure, .close = top_close,
};
static void popup_configure(void *data, struct xdg_popup *popup, int32_t x,
        int32_t y, int32_t width, int32_t height) {
    fprintf(stderr, "POPUP_ROLE_CONFIGURE x=%d y=%d w=%d h=%d\n", x, y, width, height);
}
static void popup_done(void *data, struct xdg_popup *popup) {
    fprintf(stderr, "POPUP_DONE mapped=%d\n", popup_drawn);
}
static const struct xdg_popup_listener popup_listener = {
    .configure = popup_configure, .popup_done = popup_done,
};
static void open_popup(uint32_t serial) {
    if (popup_role) return;
    popup_surface = wl_compositor_create_surface(compositor);
    popup_xdg = xdg_wm_base_get_xdg_surface(wm, popup_surface);
    xdg_surface_add_listener(popup_xdg, &surface_listener, NULL);
    struct xdg_positioner *positioner = xdg_wm_base_create_positioner(wm);
    xdg_positioner_set_size(positioner, popup_width, 190);
    xdg_positioner_set_anchor_rect(positioner, popup_anchor_x, 80, 1, 1);
    xdg_positioner_set_anchor(positioner, XDG_POSITIONER_ANCHOR_TOP_LEFT);
    xdg_positioner_set_gravity(positioner, XDG_POSITIONER_GRAVITY_BOTTOM_RIGHT);
    popup_role = xdg_surface_get_popup(popup_xdg, top_xdg, positioner);
    xdg_popup_add_listener(popup_role, &popup_listener, NULL);
    fprintf(stderr, "POPUP_GRAB_REQUEST received_button_serial=%u used_serial=%u\n", serial, serial);
    xdg_popup_grab(popup_role, seat, serial);
    wl_surface_commit(popup_surface);
    xdg_positioner_destroy(positioner);
}
static void pointer_enter(void *data, struct wl_pointer *ptr, uint32_t serial,
        struct wl_surface *surface, wl_fixed_t x, wl_fixed_t y) {
    fprintf(stderr, "POINTER_ENTER target=%s serial=%u x=%.1f y=%.1f\n",
        surface == top_surface ? "top" : surface == popup_surface ? "popup" : "other",
        serial, wl_fixed_to_double(x), wl_fixed_to_double(y));
}
static void pointer_leave(void *data, struct wl_pointer *ptr, uint32_t serial,
        struct wl_surface *surface) {
    fprintf(stderr, "POINTER_LEAVE target=%s serial=%u\n",
        surface == top_surface ? "top" : surface == popup_surface ? "popup" : "other", serial);
}
static void pointer_motion(void *data, struct wl_pointer *ptr, uint32_t time,
        wl_fixed_t x, wl_fixed_t y) {
    fprintf(stderr, "POINTER_MOTION x=%.1f y=%.1f\n", wl_fixed_to_double(x), wl_fixed_to_double(y));
}
static void pointer_button(void *data, struct wl_pointer *ptr, uint32_t serial,
        uint32_t time, uint32_t button, uint32_t state) {
    fprintf(stderr, "POINTER_BUTTON serial=%u button=%u state=%u popup=%d\n",
        serial, button, state, popup_role != NULL);
    if (state == WL_POINTER_BUTTON_STATE_PRESSED && button == 272 && !popup_role)
        open_popup(serial);
}
static void pointer_axis(void *data, struct wl_pointer *ptr, uint32_t time,
        uint32_t axis, wl_fixed_t value) {}
static void pointer_frame(void *data, struct wl_pointer *ptr) {}
static const struct wl_pointer_listener pointer_listener = {
    .enter = pointer_enter, .leave = pointer_leave, .motion = pointer_motion,
    .button = pointer_button, .axis = pointer_axis, .frame = pointer_frame,
};
static void seat_capabilities(void *data, struct wl_seat *s, uint32_t caps) {
    if ((caps & WL_SEAT_CAPABILITY_POINTER) && !pointer) {
        pointer = wl_seat_get_pointer(s);
        wl_pointer_add_listener(pointer, &pointer_listener, NULL);
    }
}
static void seat_name(void *data, struct wl_seat *s, const char *name) {}
static const struct wl_seat_listener seat_listener = {
    .capabilities = seat_capabilities, .name = seat_name,
};
static void global(void *data, struct wl_registry *reg, uint32_t name,
        const char *interface, uint32_t version) {
    if (!strcmp(interface, wl_compositor_interface.name))
        compositor = wl_registry_bind(reg, name, &wl_compositor_interface, version < 4 ? version : 4);
    else if (!strcmp(interface, wl_shm_interface.name))
        shm = wl_registry_bind(reg, name, &wl_shm_interface, 1);
    else if (!strcmp(interface, xdg_wm_base_interface.name))
        wm = wl_registry_bind(reg, name, &xdg_wm_base_interface, version < 3 ? version : 3);
    else if (!strcmp(interface, wl_seat_interface.name)) {
        seat = wl_registry_bind(reg, name, &wl_seat_interface, version < 5 ? version : 5);
        wl_seat_add_listener(seat, &seat_listener, NULL);
    }
}
static void removed(void *data, struct wl_registry *reg, uint32_t name) {}
static const struct wl_registry_listener registry_listener = {.global = global, .global_remove = removed};
static void stop(int signal_number) { running = 0; }
int main(void) {
    signal(SIGTERM, stop);
    if (getenv("PROBE_POPUP_FULLY_VISIBLE")) {
        popup_width = 250;
        popup_anchor_x = 50;
    }
    display = wl_display_connect(NULL);
    if (!display) { fprintf(stderr, "cannot connect Wayland\n"); return 1; }
    struct wl_registry *registry = wl_display_get_registry(display);
    wl_registry_add_listener(registry, &registry_listener, NULL);
    wl_display_roundtrip(display);
    wl_display_roundtrip(display);
    if (!compositor || !shm || !wm || !seat || !pointer) {
        fprintf(stderr, "missing Wayland globals\n"); return 1;
    }
    xdg_wm_base_add_listener(wm, &wm_listener, NULL);
    top_surface = wl_compositor_create_surface(compositor);
    top_xdg = xdg_wm_base_get_xdg_surface(wm, top_surface);
    xdg_surface_add_listener(top_xdg, &surface_listener, NULL);
    top_role = xdg_surface_get_toplevel(top_xdg);
    xdg_toplevel_add_listener(top_role, &top_listener, NULL);
    xdg_toplevel_set_title(top_role, "Mosaic Valid Grab Probe");
    xdg_toplevel_set_app_id(top_role, "org.mosaic.ValidGrabProbe");
    wl_surface_commit(top_surface);
    while (running && wl_display_dispatch(display) >= 0) {}
    fprintf(stderr, "CLIENT_EXIT popup_created=%d popup_mapped=%d\n", popup_role != NULL, popup_drawn);
    wl_display_disconnect(display);
    return 0;
}
