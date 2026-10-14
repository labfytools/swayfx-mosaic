#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <poll.h>
#include <signal.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>
#include <wayland-client.h>
#include "xdg-shell-client.h"

/* WHY: the compositor must wait on a real, responsive XDG client.
 * CONTRACT: hold only a received configure; ACK the latest received serial.
 * INVARIANT: Wayland dispatch and ping replies continue while ACK is held. */
static struct wl_display *display;
static struct wl_compositor *compositor;
static struct wl_shm *shm;
static struct xdg_wm_base *wm;
static struct wl_surface *surface;
static struct xdg_surface *xdg;
static struct xdg_toplevel *toplevel;
static struct wl_seat *seat;
static struct wl_pointer *pointer;
static volatile sig_atomic_t running = 1;
static bool mapped, hold_next, held;
static uint32_t latest_serial;
static int32_t width = 420, height = 320, configured_width = 420, configured_height = 320;
static unsigned generation;

static long long stamp(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

static void draw(void) {
    if (configured_width > 0) width = configured_width;
    if (configured_height > 0) height = configured_height;
    if (width <= 0 || height <= 0 || width > 4096 || height > 4096) {
        fprintf(stderr, "INVALID_SIZE %d %d\n", width, height);
        exit(2);
    }
    size_t bytes = (size_t)width * (size_t)height * 4;
    char name[] = "/tmp/mosaic-saved-shm-XXXXXX";
    int fd = mkstemp(name);
    if (fd < 0 || ftruncate(fd, (off_t)bytes) < 0) { perror("shm"); exit(2); }
    unlink(name);
    uint32_t *pixels = mmap(NULL, bytes, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (pixels == MAP_FAILED) { perror("mmap"); exit(2); }
    uint32_t color = (generation++ % 2) ? 0x0020d0a0 : 0x002344cc;
#ifdef STATIC_REFERENCE
    /* CONTRACT: H2 uses one opaque SHM color across every real configure. */
    color = 0x00303038;
#endif
    for (size_t i = 0; i < bytes / 4; ++i) pixels[i] = color;
    struct wl_shm_pool *pool = wl_shm_create_pool(shm, fd, (int)bytes);
    struct wl_buffer *buffer = wl_shm_pool_create_buffer(pool, 0, width, height,
        width * 4, WL_SHM_FORMAT_XRGB8888);
    wl_surface_attach(surface, buffer, 0, 0);
    wl_surface_damage_buffer(surface, 0, 0, width, height);
    wl_surface_commit(surface);
    fprintf(stderr, "COMMIT ns=%lld serial=%u size=%dx%d color=%08x\n",
        stamp(), latest_serial, width, height, color);
    wl_buffer_destroy(buffer);
    wl_shm_pool_destroy(pool);
    munmap(pixels, bytes);
    close(fd);
    mapped = true;
}

static void ack_and_commit(void) {
    if (!latest_serial) return;
    xdg_surface_ack_configure(xdg, latest_serial);
    fprintf(stderr, "ACK ns=%lld serial=%u size=%dx%d\n",
        stamp(), latest_serial, configured_width, configured_height);
    draw();
    held = false;
}

static void ping(void *data, struct xdg_wm_base *base, uint32_t serial) {
    xdg_wm_base_pong(base, serial);
    fprintf(stderr, "PONG ns=%lld serial=%u\n", stamp(), serial);
}
static const struct xdg_wm_base_listener wm_listener = {.ping = ping};

static void role_configure(void *data, struct xdg_toplevel *role,
        int32_t w, int32_t h, struct wl_array *states) {
    if (w > 0) configured_width = w;
    if (h > 0) configured_height = h;
    fprintf(stderr, "ROLE_CONFIGURE ns=%lld size=%dx%d\n", stamp(), w, h);
}
static void role_close(void *data, struct xdg_toplevel *role) { running = 0; }
static const struct xdg_toplevel_listener role_listener = {
    .configure = role_configure, .close = role_close,
};
static void configure(void *data, struct xdg_surface *s, uint32_t serial) {
    latest_serial = serial;
    fprintf(stderr, "XDG_CONFIGURE ns=%lld serial=%u size=%dx%d hold=%d previous=%d\n",
        stamp(), serial, configured_width, configured_height, hold_next || held, held);
    if (hold_next || held) {
        held = true;
        hold_next = false;
        fprintf(stderr, "HELD ns=%lld serial=%u\n", stamp(), serial);
    } else {
        ack_and_commit();
    }
}
static const struct xdg_surface_listener surface_listener = {.configure = configure};
static void pointer_enter(void *data, struct wl_pointer *p, uint32_t serial,
        struct wl_surface *s, wl_fixed_t x, wl_fixed_t y) {
    fprintf(stderr, "ENTER ns=%lld x=%.2f y=%.2f\n", stamp(),
        wl_fixed_to_double(x), wl_fixed_to_double(y));
}
static void pointer_leave(void *data, struct wl_pointer *p, uint32_t serial,
        struct wl_surface *s) { fprintf(stderr, "LEAVE ns=%lld\n", stamp()); }
static void pointer_motion(void *data, struct wl_pointer *p, uint32_t time,
        wl_fixed_t x, wl_fixed_t y) {
    fprintf(stderr, "MOTION ns=%lld x=%.2f y=%.2f\n", stamp(),
        wl_fixed_to_double(x), wl_fixed_to_double(y));
}
static void pointer_button(void *data, struct wl_pointer *p, uint32_t serial,
        uint32_t time, uint32_t button, uint32_t state) {
    fprintf(stderr, "BUTTON ns=%lld serial=%u button=%u state=%u\n",
        stamp(), serial, button, state);
}
static void pointer_axis(void *data, struct wl_pointer *p, uint32_t t,
        uint32_t axis, wl_fixed_t value) {}
static void pointer_frame(void *data, struct wl_pointer *p) {}
static const struct wl_pointer_listener pointer_listener = {
    .enter = pointer_enter, .leave = pointer_leave, .motion = pointer_motion,
    .button = pointer_button, .axis = pointer_axis, .frame = pointer_frame,
};
static void capabilities(void *data, struct wl_seat *s, uint32_t caps) {
    if ((caps & WL_SEAT_CAPABILITY_POINTER) && !pointer) {
        pointer = wl_seat_get_pointer(s);
        wl_pointer_add_listener(pointer, &pointer_listener, NULL);
    }
}
static void seat_name(void *data, struct wl_seat *s, const char *name) {}
static const struct wl_seat_listener seat_listener = {
    .capabilities = capabilities, .name = seat_name,
};
static void global(void *data, struct wl_registry *registry, uint32_t name,
        const char *interface, uint32_t version) {
    if (!strcmp(interface, wl_compositor_interface.name))
        compositor = wl_registry_bind(registry, name, &wl_compositor_interface, version < 4 ? version : 4);
    else if (!strcmp(interface, wl_shm_interface.name))
        shm = wl_registry_bind(registry, name, &wl_shm_interface, 1);
    else if (!strcmp(interface, xdg_wm_base_interface.name))
        wm = wl_registry_bind(registry, name, &xdg_wm_base_interface, version < 3 ? version : 3);
    else if (!strcmp(interface, wl_seat_interface.name)) {
        seat = wl_registry_bind(registry, name, &wl_seat_interface, version < 5 ? version : 5);
        wl_seat_add_listener(seat, &seat_listener, NULL);
    }
}
static void global_remove(void *data, struct wl_registry *registry, uint32_t name) {}
static const struct wl_registry_listener registry_listener = {
    .global = global, .global_remove = global_remove,
};
static void stop(int signum) { running = 0; }

int main(void) {
    signal(SIGTERM, stop);
    display = wl_display_connect(NULL);
    if (!display) { fprintf(stderr, "CONNECT_FAILED\n"); return 1; }
    struct wl_registry *registry = wl_display_get_registry(display);
    wl_registry_add_listener(registry, &registry_listener, NULL);
    wl_display_roundtrip(display);
    wl_display_roundtrip(display);
    if (!compositor || !shm || !wm) { fprintf(stderr, "MISSING_GLOBAL\n"); return 2; }
    xdg_wm_base_add_listener(wm, &wm_listener, NULL);
    surface = wl_compositor_create_surface(compositor);
    xdg = xdg_wm_base_get_xdg_surface(wm, surface);
    xdg_surface_add_listener(xdg, &surface_listener, NULL);
    toplevel = xdg_surface_get_toplevel(xdg);
    xdg_toplevel_add_listener(toplevel, &role_listener, NULL);
#ifdef STATIC_REFERENCE
    xdg_toplevel_set_title(toplevel, "Mosaic Static Reference");
    xdg_toplevel_set_app_id(toplevel, "org.mosaic.StaticReference");
#else
    xdg_toplevel_set_title(toplevel, "Mosaic Saved Buffer Probe");
    xdg_toplevel_set_app_id(toplevel, "org.mosaic.SavedBufferProbe");
#endif
    wl_surface_commit(surface);
    fprintf(stderr, "READY ns=%lld\n", stamp());
    while (running) {
        wl_display_flush(display);
        struct pollfd fds[2] = {
            {.fd = wl_display_get_fd(display), .events = POLLIN},
            {.fd = STDIN_FILENO, .events = POLLIN},
        };
        int ready = poll(fds, 2, 100);
        if (ready < 0) { if (errno == EINTR) continue; perror("poll"); break; }
        if (fds[0].revents & (POLLIN | POLLERR | POLLHUP)) {
            if (wl_display_dispatch(display) < 0) break;
        }
        if (fds[1].revents & POLLIN) {
            char cmd[64];
            if (!fgets(cmd, sizeof(cmd), stdin)) break;
            if (!strncmp(cmd, "hold_next_configure", 19)) {
                hold_next = true;
                fprintf(stderr, "COMMAND hold_next_configure DONE ns=%lld\n", stamp());
            } else if (!strncmp(cmd, "release_configure", 17)) {
                if (held) ack_and_commit();
                fprintf(stderr, "COMMAND release_configure DONE ns=%lld\n", stamp());
            } else if (!strncmp(cmd, "close", 5)) {
                running = 0;
                fprintf(stderr, "COMMAND close DONE ns=%lld\n", stamp());
            }
        }
    }
    fprintf(stderr, "EXIT ns=%lld mapped=%d held=%d error=%d\n",
        stamp(), mapped, held, wl_display_get_error(display));
    xdg_toplevel_destroy(toplevel);
    xdg_surface_destroy(xdg);
    wl_surface_destroy(surface);
    wl_display_flush(display);
    wl_display_disconnect(display);
    return 0;
}
