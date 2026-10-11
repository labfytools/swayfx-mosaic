#define _DEFAULT_SOURCE
#include <linux/input-event-codes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <wayland-client.h>
#include "virtual-pointer-client.h"
static struct zwlr_virtual_pointer_manager_v1 *manager;
static void global(void *data, struct wl_registry *registry, uint32_t name,
        const char *interface, uint32_t version) {
    if (!strcmp(interface, zwlr_virtual_pointer_manager_v1_interface.name))
        manager=wl_registry_bind(registry,name,&zwlr_virtual_pointer_manager_v1_interface,
            version < 2 ? version : 2);
}
static void removed(void *data, struct wl_registry *registry, uint32_t name) {}
int main(void) {
    struct wl_display *display=wl_display_connect(NULL);
    if (!display) return 1;
    struct wl_registry *registry=wl_display_get_registry(display);
    struct wl_registry_listener listener={global,removed};
    wl_registry_add_listener(registry,&listener,NULL);
    wl_display_roundtrip(display);
    if (!manager) return 2;
    struct zwlr_virtual_pointer_v1 *pointer=
        zwlr_virtual_pointer_manager_v1_create_virtual_pointer(manager,NULL);
    wl_display_roundtrip(display);
    fprintf(stderr,"POINTER_READY\n");fflush(stderr);
    char line[128];
    uint32_t stamp=1000;
    while (fgets(line,sizeof(line),stdin)) {
        char action[16];int x,y;
        if (sscanf(line,"%15s %d %d",action,&x,&y)!=3) continue;
        fprintf(stderr,"INJECT %s %d,%d\n",action,x,y);fflush(stderr);
        zwlr_virtual_pointer_v1_motion_absolute(pointer,stamp++,x,y,1600,600);
        zwlr_virtual_pointer_v1_frame(pointer);
        wl_display_flush(display);usleep(250000);
        if (!strcmp(action,"left") || !strcmp(action,"right")) {
            uint32_t button=!strcmp(action,"left") ? BTN_LEFT : BTN_RIGHT;
            zwlr_virtual_pointer_v1_button(pointer,stamp++,button,WL_POINTER_BUTTON_STATE_PRESSED);
            zwlr_virtual_pointer_v1_frame(pointer);
            wl_display_flush(display);usleep(80000);
            zwlr_virtual_pointer_v1_button(pointer,stamp++,button,WL_POINTER_BUTTON_STATE_RELEASED);
            zwlr_virtual_pointer_v1_frame(pointer);
            wl_display_flush(display);
        }
        wl_display_roundtrip(display);
        fprintf(stderr,"INJECT_DONE %s %d,%d\n",action,x,y);fflush(stderr);
    }
    zwlr_virtual_pointer_v1_destroy(pointer);
    zwlr_virtual_pointer_manager_v1_destroy(manager);
    wl_registry_destroy(registry);
    wl_display_disconnect(display);
    return 0;
}
