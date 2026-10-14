#ifndef SUPPORT_H
#define SUPPORT_H
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wayland-server-core.h>
#include <pixman.h>
// WHY: isolate static core functions without a compositor or GPU.
// CONTRACT: these reduced structs contain only fields read by exact slices;
// they are fixtures, never an ABI/layout assertion about wlroots or Sway.
// INVARIANT: all nodes, containers and workspace pointers are borrowed and
// live until their real Wayland destroy listeners have been emitted.
struct wlr_box { int x,y,width,height; };
enum { WLR_SCENE_NODE_TREE, WLR_SCENE_NODE_BUFFER, WLR_SCENE_NODE_RECT, WLR_SCENE_NODE_SHADOW, WLR_SCENE_NODE_OPTIMIZED_BLUR, WLR_SCENE_NODE_BLUR };
struct wlr_scene_tree;
struct wlr_scene_node { int type,x,y; struct wlr_scene_tree *parent; struct { struct wl_signal destroy; } events; bool coords_valid; };
struct wlr_scene_tree { struct wlr_scene_node node; };
struct wlr_scene_buffer { struct wlr_scene_node node; bool (*point_accepts_input)(struct wlr_scene_buffer *, double *, double *); };
struct wlr_scene_rect { struct wlr_scene_node node; bool accepts_input; struct { struct wlr_box area; } clipped_region; };
// WHY: coordinate lookup requires hierarchy but not compositor ownership.
// CONTRACT: use small fixture translations; failed lookup is injectable.
// INVARIANT: no pending geometry is substituted for applied node coordinates.
static bool wlr_scene_node_coords(struct wlr_scene_node *n,int *x,int *y) { *x=*y=0; for (;n;n=n->parent?&n->parent->node:NULL) {if(!n->coords_valid)return false; *x+=n->x; *y+=n->y;} return true; }
static bool wlr_box_contains_point(const struct wlr_box *b,double x,double y) {return x>=b->x && y>=b->y && x<(double)b->x+b->width && y<(double)b->y+b->height;}
static bool wlr_box_empty(const struct wlr_box *b) {return b->width<=0||b->height<=0;}
static struct wlr_scene_buffer *wlr_scene_buffer_from_node(struct wlr_scene_node *n) {return (struct wlr_scene_buffer *)n;}
static struct wlr_scene_rect *wlr_scene_rect_from_node(struct wlr_scene_node *n) {return (struct wlr_scene_rect *)n;}
// WHY: mutation callbacks/loggers otherwise pull in the full scene engine.
// CONTRACT: only callback invocation is counted; no render/damage claim.
// INVARIANT: stubs neither install nor remove clips/listeners.
#define WLR_INFO 1
#define WLR_ERROR 2
#define SWAY_INFO 1
#define wlr_log(level, ...) ((void)(level))
#define sway_log(level, ...) ((void)(level))
extern unsigned updates, allocations;
extern bool allocation_unavailable;
static void scene_node_update(struct wlr_scene_node *n,void *unused) {(void)n;(void)unused; updates++;}
void wlr_scene_tree_set_clip(struct wlr_scene_tree *,const struct wlr_box *);
bool wlr_scene_tree_get_clip(struct wlr_scene_tree *,struct wlr_box *);
struct wlr_scene_tree *wlr_scene_tree_from_node(struct wlr_scene_node *);
unsigned clip_count(void);
bool inside(struct wlr_scene_node *,double,double);
void intersect(struct wlr_scene_node *,pixman_region32_t *);
bool hit(struct wlr_scene_node *,double,double);
bool translate(const struct wlr_box *,int,int,struct wlr_box *);
static void init_node(struct wlr_scene_node *n,int type,struct wlr_scene_tree *parent,int x,int y) {*n=(struct wlr_scene_node){.type=type,.parent=parent,.x=x,.y=y,.coords_valid=true};wl_signal_init(&n->events.destroy);}
#endif
