#include "support.h"
unsigned updates, allocations, old_region_updates;
bool allocation_unavailable;
unsigned fail_at, publications;
static void *injected_calloc(size_t n,size_t z){ allocations++;if(allocation_unavailable || allocations==fail_at)return NULL;return calloc(n,z); }
#include "sidecar.inc"
#include "enabled.inc"
#define calloc injected_calloc
#include "setter.inc"
#ifdef MODE_C
// WHY: exact create body is compiled without publishing a native scene.
// CONTRACT: count the point at which the native implementation would attach.
// INVARIANT: failed allocations never reach this callback.
static void scene_tree_init(struct wlr_scene_tree *t,struct wlr_scene_tree *p){init_node(&t->node,WLR_SCENE_NODE_TREE,p,0,0);publications++;}
#include "create.inc"
// Fixture only: stack nodes in inherited popup tests need reserved storage.
// Native create is tested independently, including both prepublication failures.
void reserve_fixture(struct wlr_scene_tree *t){struct scene_tree_clip *e=calloc(1,sizeof(*e));assert(e);e->tree=t;e->destroy.notify=scene_tree_clip_destroy;wl_signal_add(&t->node.events.destroy,&e->destroy);e->next=scene_tree_clips;scene_tree_clips=e;}
#endif
#undef calloc
#include "clip.inc"
#include "hit.inc"
unsigned clip_count(void){unsigned n=0;for(struct scene_tree_clip *p=scene_tree_clips;p;p=p->next)n++;return n;}
bool inside(struct wlr_scene_node *n,double x,double y){return scene_node_point_inside_clip(n,x,y);}
void intersect(struct wlr_scene_node *n,pixman_region32_t *r){scene_node_intersect_clip(n,r);}
bool hit(struct wlr_scene_node *n,double x,double y){struct node_at_data d={.lx=x,.ly=y};int nx,ny;if(!wlr_scene_node_coords(n,&nx,&ny))return false;return scene_node_at_iterator(n,nx,ny,&d);}
bool translate(const struct wlr_box *b,int x,int y,struct wlr_box *g){return scene_clip_translate(b,x,y,g);}
