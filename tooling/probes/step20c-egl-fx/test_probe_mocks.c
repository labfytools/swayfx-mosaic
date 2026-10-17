/* Offline harness: every native EGL/Wayland/wlroots entrypoint is replaced.
 * This executable is NOT the real probe and links no EGL/FX/wlroots library. */
#define main probe_main
#define environ mock_environ
#define wl_event_loop_create mock_loop_create
#define wl_event_loop_destroy mock_loop_destroy
#define wlr_headless_backend_create mock_backend_create
#define wlr_backend_destroy mock_backend_destroy
#define wlr_backend_get_drm_fd mock_backend_fd
#define wlr_egl_create_with_drm_fd mock_egl_create
#define wlr_egl_destroy mock_egl_destroy
#define wlr_egl_get_display mock_egl_display
#define eglQueryString mock_query_string
#define eglGetProcAddress mock_get_proc
#define fx_renderer_create_egl mock_fx_create
#define wlr_renderer_destroy mock_renderer_destroy
#define wlr_renderer_get_drm_fd mock_renderer_fd
#define wlr_renderer_get_render_formats mock_render_formats
#define wlr_renderer_get_texture_formats mock_texture_formats
#include "probe.c"
#undef main
#include <assert.h>

static int mode, fx_calls, egl_destroyed, renderer_destroyed, order;
static unsigned texture_queries;
static struct wlr_backend backend_object;
static struct wlr_renderer renderer_object;
static struct wlr_drm_format format_object = {.format = 875713112};
static struct wlr_drm_format_set format_set = {.len = 1, .formats = &format_object};
static struct wlr_drm_format_set excessive_set = {.len = 257};
static const char *device_extensions;
static char *mock_environment[] = {
	"PATH=/usr/bin", "PWD=/tmp", "LC_ALL=C", "WLR_RENDERER_FORCE_SOFTWARE=1",
	"WLR_RENDERER_ALLOW_SOFTWARE=1", "LIBGL_ALWAYS_SOFTWARE=1", "LP_NUM_THREADS=2",
	"__EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/50_mesa.json", NULL,
};

char **mock_environ = mock_environment;

struct wl_event_loop *mock_loop_create(void) {
	return (struct wl_event_loop *)(uintptr_t)1;
}
void mock_loop_destroy(struct wl_event_loop *loop) {
	assert(loop == (struct wl_event_loop *)(uintptr_t)1 && order == 2);
	order = 3;
}
struct wlr_backend *mock_backend_create(struct wl_event_loop *loop) {
	assert(loop == (struct wl_event_loop *)(uintptr_t)1);
	return &backend_object;
}
void mock_backend_destroy(struct wlr_backend *backend) {
	assert(backend == &backend_object && order == 1);
	order = 2;
}
int mock_backend_fd(struct wlr_backend *backend) {
	assert(backend == &backend_object);
	return -1;
}
struct wlr_egl *mock_egl_create(int fd) {
	assert(fd == -1);
	return (struct wlr_egl *)(uintptr_t)2;
}
void mock_egl_destroy(struct wlr_egl *egl) {
	assert(egl == (struct wlr_egl *)(uintptr_t)2 && order == 0);
	assert(renderer_destroyed == 0);
	egl_destroyed++;
	order = 1;
}
EGLDisplay mock_egl_display(struct wlr_egl *egl) {
	assert(egl == (struct wlr_egl *)(uintptr_t)2);
	return (EGLDisplay)(uintptr_t)3;
}
const char *mock_query_string(EGLDisplay display, EGLint name) {
	if (display == EGL_NO_DISPLAY) {
		return "EGL_EXT_device_query";
	}
	assert(display == (EGLDisplay)(uintptr_t)3);
	return name == EGL_EXTENSIONS ? "EGL_EXT_image_dma_buf_import" : "mock";
}
static EGLBoolean mock_query_display(EGLDisplay display, EGLint attribute, EGLAttrib *value) {
	assert(display == (EGLDisplay)(uintptr_t)3 && attribute == EGL_DEVICE_EXT);
	*value = 4;
	return mode != 5;
}
static const char *mock_query_device(EGLDeviceEXT device, EGLint name) {
	/* An arbitrary enumerated device would violate this assertion. */
	assert(device == (EGLDeviceEXT)(uintptr_t)4 && name == EGL_EXTENSIONS);
	return device_extensions;
}
__eglMustCastToProperFunctionPointerType mock_get_proc(const char *name) {
	if (strcmp(name, "eglQueryDisplayAttribEXT") == 0) {
		return (__eglMustCastToProperFunctionPointerType)mock_query_display;
	}
	assert(strcmp(name, "eglQueryDeviceStringEXT") == 0);
	return (__eglMustCastToProperFunctionPointerType)mock_query_device;
}
struct wlr_renderer *mock_fx_create(struct wlr_egl *egl) {
	assert(egl == (struct wlr_egl *)(uintptr_t)2);
	fx_calls++;
	return mode == 1 ? NULL : &renderer_object;
}
void mock_renderer_destroy(struct wlr_renderer *renderer) {
	assert(renderer == &renderer_object && order == 0 && egl_destroyed == 0);
	renderer_destroyed++;
	/* Mock renderer consumes the transferred EGL, without a second helper free. */
	order = 1;
}
int mock_renderer_fd(struct wlr_renderer *renderer) {
	assert(renderer == &renderer_object);
	return mode == 7 ? 42 : -1;
}
const struct wlr_drm_format_set *mock_render_formats(struct wlr_renderer *renderer) {
	assert(renderer == &renderer_object);
	return mode == 6 ? &excessive_set : &format_set;
}
const struct wlr_drm_format_set *mock_texture_formats(struct wlr_renderer *renderer,
		uint32_t caps) {
	assert(renderer == &renderer_object);
	assert(caps == WLR_BUFFER_CAP_DMABUF || caps == WLR_BUFFER_CAP_DATA_PTR ||
		caps == WLR_BUFFER_CAP_SHM);
	assert((texture_queries & caps) == 0);
	texture_queries |= caps;
	return caps == WLR_BUFFER_CAP_DMABUF ? &format_set : NULL;
}

int main(void) {
	/* Keep bounded test output separate from simulated JSONL evidence. */
	assert(freopen("/dev/null", "w", stdout) != NULL);
	for (mode = 0; mode < 8; mode++) {
		fx_calls = egl_destroyed = renderer_destroyed = order = 0;
		texture_queries = 0;
		device_extensions = "EGL_MESA_device_software";
		if (mode == 2) {
			device_extensions = "EGL_EXT_device_drm";
		} else if (mode == 3) {
			device_extensions = "EGL_MESA_device_software EGL_EXT_device_drm_render_node";
		} else if (mode == 4) {
			device_extensions = "EGL_MESA_device_software_suffix";
		}
		renderer_object.render_buffer_caps = WLR_BUFFER_CAP_DMABUF;
		char *argv[] = {"inert-mock", NULL};
		assert(probe_main(1, argv) == (mode == 0 ? 0 : 20));
		assert(order == 3);
		if (mode >= 2 && mode <= 5) {
			assert(fx_calls == 0 && egl_destroyed == 1 && renderer_destroyed == 0);
		} else if (mode == 1) {
			assert(fx_calls == 1 && egl_destroyed == 1 && renderer_destroyed == 0);
		} else {
			assert(fx_calls == 1 && egl_destroyed == 0 && renderer_destroyed == 1);
		}
		if (mode == 0 || mode == 6) {
			assert(texture_queries == (WLR_BUFFER_CAP_DMABUF | WLR_BUFFER_CAP_DATA_PTR |
				WLR_BUFFER_CAP_SHM));
		}
	}
	fputs("8 mock C scenarios passed; no EGL/FX library linked\n", stderr);
	return 0;
}
