#include <stdio.h>
#include <stddef.h>
#include <stdbool.h>
#include <wayland-server-core.h>
#include <wlr/util/box.h>
struct wlr_scene_tree;
#include "size-struct.inc"
int main(void){printf("sidecar_bytes=%zu box_offset=%zu listener_offset=%zu pointer_bytes=%zu\n",sizeof(struct scene_tree_clip),offsetof(struct scene_tree_clip,box),offsetof(struct scene_tree_clip,destroy),sizeof(void *));return 0;}
