#define _GNU_SOURCE
#define _POSIX_C_SOURCE 200809L
#include "layer-shell-client.h"
#include "xdg-shell-client.h"
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
#include <sys/resource.h>
#include <sys/prctl.h>

/* WHY: one persistent background supplies real A/B commits below blur_tree.
 * CONTRACT: fixed opaque background, premultiplied ARGB glass and static H2.
 * INVARIANT: no animation, synthetic configure, popup or held transaction. */
static struct wl_display *display;
static struct wl_compositor *compositor;
static struct wl_shm *shm;
static struct xdg_wm_base *wm;
static struct zwlr_layer_shell_v1 *shell;
static struct wl_output *h1;
static struct wl_surface *surface;
static struct xdg_surface *xdg;
static struct xdg_toplevel *top;
static struct zwlr_layer_surface_v1 *layer;
static const char *mode;
static int width = 420, height = 320;
static unsigned commits, live_buffers, released_buffers;
static char pattern = 'A';
/* G3 new explicit source command protocol; first A bytes retained verbatim. */
static unsigned char *source_a;
static size_t source_a_size;
static const char *source_command;
static uint32_t source_crc(const unsigned char *p,size_t n) {
  uint32_t crc=~0u;
  for(size_t i=0;i<n;i++) {crc^=p[i];for(int b=0;b<8;b++)crc=(crc>>1)^((0u-(crc&1u))&0xedb88320u);}
  return ~crc;
}
static volatile sig_atomic_t running = 1;
struct pixels {
  struct wl_buffer *buffer;
  void *map;
  size_t size;
  struct pixels *next;
};
static struct pixels *buffers;
static long long stamp(void) {
  struct timespec t;
  clock_gettime(CLOCK_MONOTONIC, &t);
  return (long long)t.tv_sec * 1000000000LL + t.tv_nsec;
}
static void free_pixels(struct pixels *p) {
  struct pixels **it = &buffers;
  while (*it && *it != p)
    it = &(*it)->next;
  if (*it)
    *it = p->next;
  wl_buffer_destroy(p->buffer);
  munmap(p->map, p->size);
  free(p);
  --live_buffers;
}
static void release(void *data, struct wl_buffer *b) {
  ++released_buffers;
  fprintf(stderr, "RELEASE ns=%lld buffer=%u\n", stamp(),
          wl_proxy_get_id((struct wl_proxy *)b));
  free_pixels(data);
}
static const struct wl_buffer_listener buffer_listener = {.release = release};
static void draw(void) {
  /* CONTRACT: exactly one runner command per reserved A/B image.
   * INVARIANT: configures cannot draw, and the sequence is A/B/A only. */
  if (!strcmp(mode, "background") &&
      (width != 800 || height != 600 || commits >= 3 ||
       pattern != (commits == 1 ? 'B' : 'A')))
    exit(2);
  if (width <= 0 || height <= 0 || width > 4096 || height > 4096 ||
      live_buffers >= 8)
    exit(2);
  size_t size = (size_t)width * (size_t)height * 4;
  /* CONTRACT: each mapping stays immutable until native wl_buffer.release.
   * Bounds keep pool/stride integers valid, with at most eight outstanding. */
  char name[512];
  const char *runtime = getenv("TMPDIR");
  if (!runtime || strcmp(runtime,"/var/tmp/swayfx-mosaic-corec-v2-i516p6po/scratch") || snprintf(name, sizeof(name), "%s/g2-shm-XXXXXX", runtime) >=
                      (int)sizeof(name))
    exit(2);
  int fd = mkstemp(name);
  if (fd < 0)
    exit(2);
  unlink(name);
  if (ftruncate(fd, (off_t)size) < 0)
    exit(2);
  struct pixels *p = calloc(1, sizeof(*p));
  if (!p)
    exit(2);
  p->map = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
  p->size = size;
  if (p->map == MAP_FAILED)
    exit(2);
  uint32_t *pixels = p->map;
  for (int y = 0; y < height; ++y)
    for (int x = 0; x < width; ++x) {
      uint32_t color = 0x00303038;
      if (!strcmp(mode, "background"))
        color = pattern == 'A' ? (x / 8 % 2 ? 0x000f192d : 0x00f5f5f5)
                               : (x / 8 % 2 ? 0x00b02040 : 0x0020c0e0);
      else if (!strcmp(mode, "glass"))
        color = 0x88442010;
      else if (!strcmp(mode, "filler"))
        color = 0x00000000;
      pixels[(size_t)y * (size_t)width + (size_t)x] = color;
    }
  if (!strcmp(mode,"background")) {
    if (!commits) {
      source_a=malloc(size);if(!source_a)exit(2);
      memcpy(source_a,p->map,size);source_a_size=size;
    } else if (commits==2) {
      if(!source_a || source_a_size!=size)exit(2);
      /* A-return is the preserved original payload, not a fitted redraw. */
      memcpy(p->map,source_a,size);
    } else if(source_a_size==size && !memcmp(source_a,p->map,size)) exit(2);
    fprintf(stderr,"G3_SOURCE_BYTES command=%s bytes=%zu crc32=%08x exact_original=%s\n",
      source_command,size,source_crc(p->map,size),commits==2?"true":"not-return");
  }
  struct wl_shm_pool *pool = wl_shm_create_pool(shm, fd, (int)size);
  p->buffer = wl_shm_pool_create_buffer(
      pool, 0, width, height, width * 4,
      (!strcmp(mode, "glass") || !strcmp(mode, "filler"))
          ? WL_SHM_FORMAT_ARGB8888
          : WL_SHM_FORMAT_XRGB8888);
  p->next = buffers;
  buffers = p;
  ++live_buffers;
  wl_buffer_add_listener(p->buffer, &buffer_listener, p);
  wl_surface_attach(surface, p->buffer, 0, 0);
  wl_surface_damage_buffer(surface, 0, 0, width, height);
  wl_surface_commit(surface);
  fprintf(stderr,
          "CLIENT_COMMIT ns=%lld mode=%s surface=%u buffer=%u index=%u "
          "pattern=%c size=%dx%d damage=0,0,%d,%d\n",
          stamp(), mode, wl_proxy_get_id((struct wl_proxy *)surface),
          wl_proxy_get_id((struct wl_proxy *)p->buffer), ++commits, pattern,
          width, height, width, height);
  wl_shm_pool_destroy(pool);
  close(fd);
}
static void ping(void *d, struct xdg_wm_base *b, uint32_t s) {
  xdg_wm_base_pong(b, s);
}
static const struct xdg_wm_base_listener wm_listener = {.ping = ping};
static void top_configure(void *d, struct xdg_toplevel *t, int32_t w, int32_t h,
                          struct wl_array *a) {
  if (w > 0)
    width = w;
  if (h > 0)
    height = h;
}
static void top_close(void *d, struct xdg_toplevel *t) { running = 0; }
static const struct xdg_toplevel_listener top_listener = {
    .configure = top_configure, .close = top_close};
static void configure(void *d, struct xdg_surface *s, uint32_t serial) {
  xdg_surface_ack_configure(s, serial);
  draw();
}
static const struct xdg_surface_listener xdg_listener = {.configure =
                                                             configure};
/* CONTRACT: configures ACK geometry, never submit an unreserved image.
 * WHY: duplicate layer configures must not spend autonomous mutations.
 * INVARIANT: the runner reserves then sends every A/B draw command. */
static void layer_configure(void *d, struct zwlr_layer_surface_v1 *s,
                            uint32_t serial, uint32_t w, uint32_t h) {
  if (w == 0 || h == 0 || w > 4096 || h > 4096)
    exit(2);
  if (commits && ((int)w != width || (int)h != height))
    exit(2);
  width = (int)w;
  height = (int)h;
  zwlr_layer_surface_v1_ack_configure(s, serial);
  fprintf(stderr, "BACKGROUND_CONFIGURED ns=%lld serial=%u size=%dx%d\n",
          stamp(), serial, width, height);
}
static void layer_close(void *d, struct zwlr_layer_surface_v1 *s) {
  running = 0;
}
static const struct zwlr_layer_surface_v1_listener layer_listener = {
    .configure = layer_configure, .closed = layer_close};
static void output_name(void *d, struct wl_output *o, const char *name) {
  if (!strcmp(name, "HEADLESS-1"))
    h1 = o;
}
static void output_geometry(void *d, struct wl_output *o, int32_t x, int32_t y,
                            int32_t w, int32_t h, int32_t sp, const char *m,
                            const char *n, int32_t tr) {}
static void output_mode(void *d, struct wl_output *o, uint32_t flags, int32_t w,
                        int32_t h, int32_t refresh) {}
static void output_done(void *d, struct wl_output *o) {}
static void output_scale(void *d, struct wl_output *o, int32_t scale) {}
static void output_description(void *d, struct wl_output *o, const char *desc) {
}
static const struct wl_output_listener output_listener = {
    .geometry = output_geometry,
    .mode = output_mode,
    .done = output_done,
    .scale = output_scale,
    .name = output_name,
    .description = output_description};
static void global(void *d, struct wl_registry *r, uint32_t id,
                   const char *name, uint32_t v) {
  if (!strcmp(name, "wl_compositor"))
    compositor =
        wl_registry_bind(r, id, &wl_compositor_interface, v < 4 ? v : 4);
  else if (!strcmp(name, "wl_shm"))
    shm = wl_registry_bind(r, id, &wl_shm_interface, 1);
  else if (!strcmp(name, "xdg_wm_base"))
    wm = wl_registry_bind(r, id, &xdg_wm_base_interface, v < 3 ? v : 3);
  else if (!strcmp(name, "zwlr_layer_shell_v1"))
    shell =
        wl_registry_bind(r, id, &zwlr_layer_shell_v1_interface, v < 2 ? v : 2);
  else if (!strcmp(name, "wl_output") && v >= 4) {
    struct wl_output *o = wl_registry_bind(r, id, &wl_output_interface, 4);
    wl_output_add_listener(o, &output_listener, NULL);
  }
}
static void removed(void *d, struct wl_registry *r, uint32_t id) {}
static const struct wl_registry_listener registry_listener = {
    .global = global, .global_remove = removed};
static void stop(int s) { running = 0; }
int main(int argc, char **argv) {
  /* WHY: Linux may route core dumps through a pipe handler that execs another
   * process, so a zero RLIMIT_CORE alone does not protect this client.
   * CONTRACT/INVARIANT: establish both limits before any Wayland operation. */
  struct rlimit no_core = {0, 0};
  if (setrlimit(RLIMIT_CORE, &no_core) < 0) {
    perror("setrlimit(RLIMIT_CORE)");
    return 1;
  }
  if (prctl(PR_SET_DUMPABLE, 0) < 0) {
    perror("prctl(PR_SET_DUMPABLE, 0)");
    return 1;
  }
  int dumpable = prctl(PR_GET_DUMPABLE);
  if (dumpable < 0) {
    perror("prctl(PR_GET_DUMPABLE)");
    return 1;
  }
  if (dumpable != 0) {
    fprintf(stderr, "PR_GET_DUMPABLE returned %d; expected 0\n", dumpable);
    return 1;
  }
  if (argc != 2)
    return 2;
  mode = argv[1];
  if (strcmp(mode, "background") && strcmp(mode, "glass") &&
      strcmp(mode, "filler") && strcmp(mode, "reference"))
    return 2;
  signal(SIGTERM, stop);
  display = wl_display_connect(NULL);
  if (!display)
    return 1;
  struct wl_registry *r = wl_display_get_registry(display);
  wl_registry_add_listener(r, &registry_listener, NULL);
  if (wl_display_roundtrip(display) < 0 || wl_display_roundtrip(display) < 0)
    return 1;
  if (!compositor || !shm || !wm)
    return 2;
  xdg_wm_base_add_listener(wm, &wm_listener, NULL);
  surface = wl_compositor_create_surface(compositor);
  if (!strcmp(mode, "background")) {
    if (!shell || !h1)
      return 2;
    layer = zwlr_layer_shell_v1_get_layer_surface(
        shell, surface, h1, ZWLR_LAYER_SHELL_V1_LAYER_BACKGROUND,
        "mosaic-dynamic-background");
    zwlr_layer_surface_v1_add_listener(layer, &layer_listener, NULL);
    zwlr_layer_surface_v1_set_size(layer, 0, 0);
    zwlr_layer_surface_v1_set_anchor(layer,
                                     ZWLR_LAYER_SURFACE_V1_ANCHOR_TOP |
                                         ZWLR_LAYER_SURFACE_V1_ANCHOR_BOTTOM |
                                         ZWLR_LAYER_SURFACE_V1_ANCHOR_LEFT |
                                         ZWLR_LAYER_SURFACE_V1_ANCHOR_RIGHT);
    zwlr_layer_surface_v1_set_exclusive_zone(layer, -1);
    zwlr_layer_surface_v1_set_keyboard_interactivity(layer, 0);
  } else {
    xdg = xdg_wm_base_get_xdg_surface(wm, surface);
    xdg_surface_add_listener(xdg, &xdg_listener, NULL);
    top = xdg_surface_get_toplevel(xdg);
    xdg_toplevel_add_listener(top, &top_listener, NULL);
    const char *app = !strcmp(mode, "reference") ? "org.mosaic.StaticReference"
                      : !strcmp(mode, "glass")   ? "org.mosaic.BlurGlass"
                                                 : "org.mosaic.BlurFiller";
    xdg_toplevel_set_app_id(top, app);
    xdg_toplevel_set_title(top, app);
  }
  wl_surface_commit(surface);
  while (running) {
    if (wl_display_dispatch_pending(display) < 0)
      break;
    if (wl_display_flush(display) < 0 && errno != EAGAIN)
      break;
    struct pollfd fds[2] = {
        {.fd = wl_display_get_fd(display), .events = POLLIN},
        {.fd = STDIN_FILENO, .events = POLLIN}};
    int n = poll(fds, 2, 100);
    if (n < 0) {
      if (errno == EINTR)
        continue;
      break;
    }
    if (fds[0].revents & (POLLIN | POLLERR | POLLHUP))
      if (wl_display_dispatch(display) < 0)
        break;
    if (fds[1].revents & POLLIN) {
      char cmd[64];
      if (!fgets(cmd, sizeof(cmd), stdin))
        break;
      if (!strcmp(mode, "background") &&
          ((!commits && !strcmp(cmd,"G3-A\n")) ||
           (commits==1 && !strcmp(cmd,"G3-B\n")) ||
           (commits==2 && !strcmp(cmd,"G3-A-return\n")))) {
        pattern = commits==1?'B':'A';
        source_command=commits==0?"G3-A":commits==1?"G3-B":"G3-A-return";
        draw();
        fprintf(stderr, "COMMAND %c DONE ns=%lld\n", pattern, stamp());
      } else if (!strcmp(cmd, "close\n")) {
        fprintf(stderr,"CLOSE_RECEIVED\n");running = 0;
      }
      else if(!strcmp(mode,"background"))return 2;
    }
  }
  int error = wl_display_get_error(display);
  fprintf(stderr, "EXIT ns=%lld mode=%s error=%d commits=%u\n", stamp(), mode,
          error, commits);
  if (layer)
    zwlr_layer_surface_v1_destroy(layer);
  if (top)
    xdg_toplevel_destroy(top);
  if (xdg)
    xdg_surface_destroy(xdg);
  wl_surface_destroy(surface);
  wl_display_roundtrip(display);
  fprintf(stderr,"SHM_CLOSURE created=%u released=%u\n",commits,released_buffers);
  bool all_released=commits==released_buffers;
  wl_display_flush(display);
  while (buffers)
    free_pixels(buffers);
  free(source_a);
  wl_registry_destroy(r);
  wl_display_disconnect(display);
  return error || !all_released ? 1 : 0;
}
