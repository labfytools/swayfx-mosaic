#define _POSIX_C_SOURCE 200809L
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wayland-server-core.h>
#include <wlr/backend/headless.h>
#include <wlr/render/drm_format_set.h>
#include <wlr/render/egl.h>
#include <wlr/render/wlr_renderer.h>
#include <wlr/types/wlr_buffer.h>
/* CONTRACT: existing pinned internal declarations, never private layouts. */
#include "render/egl.h"
#include "render/fx_renderer/fx_renderer.h"
#include "render/wlr_renderer.h"

extern char **environ;
static const char *const environment[] = {
	"PATH=/usr/bin", "PWD=/tmp", "LC_ALL=C",
	"WLR_RENDERER_FORCE_SOFTWARE=1", "WLR_RENDERER_ALLOW_SOFTWARE=1",
	"LIBGL_ALWAYS_SOFTWARE=1", "LP_NUM_THREADS=2",
	"__EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/50_mesa.json",
};

static bool guard_environment(void) {
	size_t count = 0;
	for (char **entry = environ; *entry != NULL; entry++) {
		bool found = false;
		for (size_t i = 0; i < sizeof(environment) / sizeof(environment[0]); i++) {
			found |= strcmp(*entry, environment[i]) == 0;
		}
		if (!found) {
			return false;
		}
		count++;
	}
	if (count != sizeof(environment) / sizeof(environment[0])) {
		return false;
	}
	/* Duplicates cannot replace a required variable. */
	for (size_t i = 0; i < sizeof(environment) / sizeof(environment[0]); i++) {
		bool found = false;
		for (char **entry = environ; *entry != NULL; entry++) {
			found |= strcmp(*entry, environment[i]) == 0;
		}
		if (!found) {
			return false;
		}
	}
	return true;
}

static bool bounded(const char *value) {
	return value != NULL && strnlen(value, 16385) <= 16384;
}

static bool extension(const char *list, const char *name) {
	size_t length = strlen(name);
	for (const char *at = list; (at = strstr(at, name)) != NULL; at += length) {
		if ((at == list || at[-1] == ' ') &&
				(at[length] == '\0' || at[length] == ' ')) {
			return true;
		}
	}
	return false;
}

static void json_string(const char *value) {
	putchar('"');
	for (const unsigned char *at = (const unsigned char *)value; *at; at++) {
		if (*at == '"' || *at == '\\') {
			printf("\\%c", *at);
		} else if (*at < 32 || *at >= 127) {
			printf("\\u%04x", *at);
		} else {
			putchar(*at);
		}
	}
	putchar('"');
}

static bool formats_valid(const struct wlr_drm_format_set *set) {
	/* NULL means this buffer capability is unsupported; sets remain borrowed. */
	if (set == NULL) {
		return true;
	}
	if (set->len > 256 || (set->len && set->formats == NULL)) {
		return false;
	}
	for (size_t i = 0; i < set->len; i++) {
		const struct wlr_drm_format *format = &set->formats[i];
		if (format->len > 64 || (format->len && format->modifiers == NULL)) {
			return false;
		}
	}
	return true;
}

static void formats_print(const char *name, const struct wlr_drm_format_set *set) {
	printf("{\"stage\":\"formats\",\"usage\":");
	json_string(name);
	printf(",\"supported\":%s,\"formats\":[", set ? "true" : "false");
	for (size_t i = 0; set && i < set->len; i++) {
		const struct wlr_drm_format *format = &set->formats[i];
		printf("%s{\"fourcc\":%u,\"modifiers\":[", i ? "," : "", format->format);
		for (size_t j = 0; j < format->len; j++) {
			/* Strings preserve all 64 bits in JSON consumers. */
			printf("%s\"%016llx\"", j ? "," : "",
				(unsigned long long)format->modifiers[j]);
		}
		printf("]}");
	}
	puts("]}");
}

int main(int argc, char **argv) {
	(void)argv;
	int status = 20; /* 0: measurement complete; 20: refused/incomplete. */
	const char *reason = "environnement_non_conforme";
	struct wl_event_loop *loop = NULL;
	struct wlr_backend *backend = NULL;
	struct wlr_egl *egl = NULL;
	struct wlr_renderer *renderer = NULL;
	if (argc != 1 || !guard_environment()) {
		goto cleanup;
	}
	reason = "creation_event_loop";
	if ((loop = wl_event_loop_create()) == NULL) {
		goto cleanup;
	}
	reason = "creation_backend";
	if ((backend = wlr_headless_backend_create(loop)) == NULL) {
		goto cleanup;
	}
	reason = "creation_egl_logiciel";
	if ((egl = wlr_egl_create_with_drm_fd(-1)) == NULL) {
		goto cleanup;
	}
	EGLDisplay display = wlr_egl_get_display(egl);
	const char *client = eglQueryString(EGL_NO_DISPLAY, EGL_EXTENSIONS);
	const char *vendor = eglQueryString(display, EGL_VENDOR);
	const char *version = eglQueryString(display, EGL_VERSION);
	const char *extensions = eglQueryString(display, EGL_EXTENSIONS);
	reason = "identite_egl_absente_ou_trop_longue";
	if (display == EGL_NO_DISPLAY || !bounded(client) || !bounded(vendor) ||
			!bounded(version) || !bounded(extensions) || !*vendor || !*version) {
		goto cleanup;
	}
	reason = "device_query_absent";
	if (!extension(client, "EGL_EXT_device_query") &&
			!extension(client, "EGL_EXT_device_base")) {
		goto cleanup;
	}
	PFNEGLQUERYDISPLAYATTRIBEXTPROC query_display =
		(PFNEGLQUERYDISPLAYATTRIBEXTPROC)eglGetProcAddress("eglQueryDisplayAttribEXT");
	PFNEGLQUERYDEVICESTRINGEXTPROC query_device =
		(PFNEGLQUERYDEVICESTRINGEXTPROC)eglGetProcAddress("eglQueryDeviceStringEXT");
	EGLAttrib device_attribute = 0;
	reason = "device_selectionne_non_identifiable";
	if (!query_display || !query_device ||
			!query_display(display, EGL_DEVICE_EXT, &device_attribute) ||
			device_attribute == 0) {
		goto cleanup;
	}
	/* WHY: inspect the display's device, never an unrelated enumerated device. */
	const char *device_extensions = query_device((EGLDeviceEXT)device_attribute,
		EGL_EXTENSIONS);
	if (!bounded(device_extensions)) {
		goto cleanup;
	}
	bool software = extension(device_extensions, "EGL_MESA_device_software");
	bool drm = extension(device_extensions, "EGL_EXT_device_drm") ||
		extension(device_extensions, "EGL_EXT_device_drm_render_node");
	printf("{\"stage\":\"egl_selected\",\"vendor\":"); json_string(vendor);
	printf(",\"version\":"); json_string(version);
	printf(",\"extensions\":"); json_string(extensions);
	printf(",\"client_extensions\":"); json_string(client);
	printf(",\"device_extensions\":"); json_string(device_extensions);
	printf(",\"selected_device_software\":%s,\"selected_device_drm\":%s}\n",
		software ? "true" : "false", drm ? "true" : "false");
	/* Evidence survives a constructor failure or a supervisor timeout. */
	if (fflush(stdout) != 0) {
		reason = "sortie_egl";
		goto cleanup;
	}
	reason = "device_non_logiciel_ou_drm";
	if (!software || drm) {
		goto cleanup;
	}
	reason = "creation_fx";
	if ((renderer = fx_renderer_create_egl(egl)) == NULL) {
		goto cleanup;
	}
	/* INVARIANT: success transfers ownership; destroy renderer OR EGL. */
	egl = NULL;
	int backend_fd = wlr_backend_get_drm_fd(backend);
	int renderer_fd = wlr_renderer_get_drm_fd(renderer);
	reason = "fd_drm_inattendu";
	if (backend_fd != -1 || renderer_fd != -1) {
		goto cleanup;
	}
	const struct wlr_drm_format_set *sets[] = {
		wlr_renderer_get_render_formats(renderer),
		wlr_renderer_get_texture_formats(renderer, WLR_BUFFER_CAP_DMABUF),
		wlr_renderer_get_texture_formats(renderer, WLR_BUFFER_CAP_DATA_PTR),
		wlr_renderer_get_texture_formats(renderer, WLR_BUFFER_CAP_SHM),
	};
	const char *names[] = {"render_target", "texture_dmabuf", "texture_data_ptr", "texture_shm"};
	reason = "formats_hors_bornes";
	size_t modifiers = 0;
	for (size_t i = 0; i < 4; i++) {
		if (!formats_valid(sets[i])) {
			goto cleanup;
		}
		for (size_t j = 0; sets[i] && j < sets[i]->len; j++) {
			modifiers += sets[i]->formats[j].len;
		}
	}
	if (modifiers > 4096) {
		goto cleanup;
	}
	for (size_t i = 0; i < 4; i++) {
		formats_print(names[i], sets[i]);
	}
	bool blocked = renderer->render_buffer_caps == WLR_BUFFER_CAP_DMABUF;
	printf("{\"stage\":\"measurement\",\"backend_drm_fd\":%d,"
		"\"renderer_drm_fd\":%d,\"backend_buffer_caps\":%u,"
		"\"renderer_render_buffer_caps\":%u,\"target_allocation\":\"NOT_ATTEMPTED\","
		"\"allocator_eligibility\":\"%s\"}\n", backend_fd, renderer_fd,
		backend->buffer_caps, renderer->render_buffer_caps,
		blocked ? "PINNED_DMABUF_ROUTE_BLOCKED_WITHOUT_DRM_OR_UDMABUF" : "UNDETERMINED");
	status = 0;
	reason = "mesure_terminee_allocation_non_tentee";
cleanup:
	if (renderer != NULL) {
		wlr_renderer_destroy(renderer);
	} else if (egl != NULL) {
		wlr_egl_destroy(egl);
	}
	if (backend != NULL) {
		wlr_backend_destroy(backend);
	}
	if (loop != NULL) {
		wl_event_loop_destroy(loop);
	}
	printf("{\"stage\":\"completion\",\"status\":%d,\"reason\":", status);
	json_string(reason);
	puts("}");
	return fflush(stdout) == 0 && !ferror(stdout) ? status : 20;
}
