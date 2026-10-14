#include "support.h"
unsigned updates, allocations;
bool allocation_unavailable;
#include "sidecar.inc"
// WHY: make only the sidecar allocation deterministically unavailable.
// CONTRACT: macro scope is solely the exact setter/getter extracted slice.
// INVARIANT: Wayland, Pixman, libc and all other allocations are untouched.
static void *sidecar_calloc(size_t n,size_t size) {allocations++; if(allocation_unavailable)return NULL;return calloc(n,size);}
#define calloc sidecar_calloc
#include "setter.inc"
#undef calloc
#include "clip.inc"
#include "hit.inc"
unsigned clip_count(void) {unsigned n=0;for(struct scene_tree_clip *p=scene_tree_clips;p;p=p->next)n++;return n;}
bool inside(struct wlr_scene_node *n,double x,double y){return scene_node_point_inside_clip(n,x,y);}
void intersect(struct wlr_scene_node *n,pixman_region32_t *r){scene_node_intersect_clip(n,r);}
bool hit(struct wlr_scene_node *n,double x,double y){struct node_at_data d={.lx=x,.ly=y};int nx,ny;assert(wlr_scene_node_coords(n,&nx,&ny));return scene_node_at_iterator(n,nx,ny,&d);}
bool translate(const struct wlr_box *b,int x,int y,struct wlr_box *g){return scene_clip_translate(b,x,y,g);}
