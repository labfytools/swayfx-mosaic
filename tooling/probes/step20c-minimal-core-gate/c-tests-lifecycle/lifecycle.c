#include "support.h"
// WHY: popup ownership is tested without transaction/scene construction.
// CONTRACT: each reduced state exposes precisely the fields used by popup.inc.
// INVARIANT: current ancestry is distinct from deliberately contradictory pending state.
enum {L_STANDARD,L_MOSAIC,FULLSCREEN_NONE=0,FULLSCREEN_WORKSPACE=1};
struct sway_workspace;
struct sway_container {struct {struct sway_workspace *workspace;struct sway_container *parent;int fullscreen_mode;} current,pending; struct {int current_width,current_height;} animation_state;struct wlr_scene_tree *scene_tree;};
struct list {void **items;int length;};
static int list_find(struct list *l,void *p){for(int i=0;i<l->length;i++)if(l->items[i]==p)return i;return -1;}
struct sway_output {int lx,ly,width,height;struct {struct sway_workspace *active_workspace;} current;};
struct sway_workspace {struct {int layout;struct list *tiling;struct sway_container *fullscreen;struct sway_output *output;} current;void *mosaic;struct {struct wlr_scene_tree *tiling;} layers;};
struct sway_view {struct sway_container *container;};
struct sway_popup_desc {struct sway_view *view;};
#include "popup.inc"
static unsigned input_calls;
static bool input(struct wlr_scene_buffer *b,double *x,double *y){(void)b;(void)x;(void)y;input_calls++;return true;}
static void expect_box(struct wlr_scene_tree *t,int x,int y,int w,int h){struct wlr_box b;assert(wlr_scene_tree_get_clip(t,&b));assert(b.x==x&&b.y==y&&b.width==w&&b.height==h);}
static void destroy(struct wlr_scene_tree *t){wl_signal_emit_mutable(&t->node.events.destroy,NULL);assert(wl_list_empty(&t->node.events.destroy.listener_list));}
// WHY: native Pixman may retain a zero-area rectangle as a nonempty region.
// CONTRACT: masking requires zero pixels, not a particular region encoding.
// INVARIANT: any rectangle with positive width AND height fails this check.
static bool has_pixels(pixman_region32_t *r){int count;pixman_box32_t *boxes=pixman_region32_rectangles(r,&count);for(int i=0;i<count;i++)if(boxes[i].x2>boxes[i].x1&&boxes[i].y2>boxes[i].y1)return true;return false;}
static void lifecycle(void){
 struct wlr_scene_tree p,c;init_node(&p.node,WLR_SCENE_NODE_TREE,NULL,10,20);init_node(&c.node,WLR_SCENE_NODE_TREE,&p,5,5);
 struct wlr_scene_buffer leaf={.point_accepts_input=input};init_node(&leaf.node,WLR_SCENE_NODE_BUFFER,&c,0,0);
 struct wlr_box out,b={0,0,100,100};assert(!wlr_scene_tree_get_clip(&p,&out));wlr_scene_tree_set_clip(&p,NULL);assert(updates==0&&allocations==0);
 wlr_scene_tree_set_clip(&p,&b);assert(allocations==1&&clip_count()==1&&wl_list_length(&p.node.events.destroy.listener_list)==1);
 b.width=80;wlr_scene_tree_set_clip(&p,&b);assert(allocations==1&&clip_count()==1&&updates==2&&wl_list_length(&p.node.events.destroy.listener_list)==1);
 wlr_scene_tree_set_clip(&p,&b);assert(updates==2);b.width=1;expect_box(&p,0,0,80,100);
 b=(struct wlr_box){0,0,100,20};wlr_scene_tree_set_clip(&c,&b);assert(clip_count()==2);
 assert(inside(&leaf.node,16,26));assert(!inside(&leaf.node,95,30));assert(hit(&leaf.node,16,26)&&input_calls==1);assert(!hit(&leaf.node,95,30)&&input_calls==1);
 pixman_region32_t r;pixman_region32_init_rect(&r,-100,-100,400,400);intersect(&leaf.node,&r);pixman_box32_t *ext=pixman_region32_extents(&r);assert(ext->x1==15&&ext->y1==25&&ext->x2==90&&ext->y2==45);pixman_region32_fini(&r);
 b=(struct wlr_box){0};wlr_scene_tree_set_clip(&c,&b);expect_box(&c,0,0,0,0);assert(!hit(&leaf.node,16,26)&&input_calls==1);
 pixman_region32_init_rect(&r,0,0,100,100);intersect(&leaf.node,&r);assert(!has_pixels(&r));pixman_region32_fini(&r);
 wlr_scene_tree_set_clip(&c,NULL);assert(!wlr_scene_tree_get_clip(&c,&out)&&clip_count()==1);unsigned before=updates;wlr_scene_tree_set_clip(&c,NULL);assert(updates==before);assert(hit(&leaf.node,16,26)&&input_calls==2);
 wlr_scene_tree_set_clip(&c,&b);destroy(&p);assert(clip_count()==1);destroy(&c);assert(clip_count()==0);
 b=(struct wlr_box){1,2,3,4};assert(translate(&b,10,20,&out)&&out.x==11&&out.y==22);assert(!translate(&b,INT_MAX,0,&out));b.width=-1;assert(!translate(&b,0,0,&out));
 // Exact translation rejection must empty render region and reject input too.
 b=(struct wlr_box){INT_MAX,0,1,1};wlr_scene_tree_set_clip(&p,&b);assert(!inside(&p.node,0,0));pixman_region32_init_rect(&r,0,0,10,10);intersect(&p.node,&r);assert(!has_pixels(&r));pixman_region32_fini(&r);destroy(&p);
 puts("PASS lifecycle: NULL/zero/copy/idempotence/single allocation/listener/removal/native destroy/native Pixman/inherited hit-before-input/translation rejection");
}
static void popups(void){
 struct wlr_scene_tree tiling,owner_scene,popup,nested;init_node(&tiling.node,WLR_SCENE_NODE_TREE,NULL,10,20);init_node(&owner_scene.node,WLR_SCENE_NODE_TREE,NULL,20,30);init_node(&popup.node,WLR_SCENE_NODE_TREE,NULL,25,35);init_node(&nested.node,WLR_SCENE_NODE_TREE,&popup,0,0);
 struct sway_output output={.width=200,.height=200};struct sway_container parent={.scene_tree=&owner_scene,.animation_state={30,30}},child={0};void *items[]={&parent};struct list list={items,1};struct sway_workspace ws={.current={.layout=L_MOSAIC,.tiling=&list,.output=&output},.mosaic=&ws,.layers={&tiling}};output.current.active_workspace=&ws;child.current.workspace=&ws;child.current.parent=&parent;struct sway_view view={&child};struct sway_popup_desc desc={&view};struct wlr_box b={0,0,100,100},out;wlr_scene_tree_set_clip(&tiling,&b);
 child.pending.fullscreen_mode=FULLSCREEN_WORKSPACE;probe_clip_popup(&popup.node,&desc);expect_box(&popup,-15,-15,100,100);assert(inside(&nested.node,30,40)&&!inside(&nested.node,150,40));
 parent.current.fullscreen_mode=FULLSCREEN_WORKSPACE;probe_clip_popup(&popup.node,&desc);assert(!wlr_scene_tree_get_clip(&popup,&out));parent.current.fullscreen_mode=FULLSCREEN_NONE;
 ws.current.layout=L_STANDARD;probe_clip_popup(&popup.node,&desc);assert(!wlr_scene_tree_get_clip(&popup,&out));ws.current.layout=L_MOSAIC;
 output.current.active_workspace=NULL;probe_clip_popup(&popup.node,&desc);expect_box(&popup,0,0,0,0);output.current.active_workspace=&ws;
 owner_scene.node.x=150;probe_clip_popup(&popup.node,&desc);expect_box(&popup,0,0,0,0);assert(!inside(&nested.node,30,40));owner_scene.node.x=20;probe_clip_popup(&popup.node,&desc);expect_box(&popup,-15,-15,100,100);
 ws.current.fullscreen=&parent;probe_clip_popup(&popup.node,&desc);assert(!wlr_scene_tree_get_clip(&popup,&out));ws.current.fullscreen=NULL;
 list.length=0;probe_clip_popup(&popup.node,&desc);assert(!wlr_scene_tree_get_clip(&popup,&out));list.length=1;
 wlr_scene_tree_set_clip(&tiling,NULL);probe_clip_popup(&popup.node,&desc);expect_box(&popup,0,0,0,0);
 desc.view=NULL;probe_clip_popup(&popup.node,&desc);assert(!wlr_scene_tree_get_clip(&popup,&out));destroy(&tiling);destroy(&popup);destroy(&nested);destroy(&owner_scene);assert(clip_count()==0);
 puts("PASS popup: real root clip/current fullscreen ancestor/pending contradiction/standard/inactive/hidden owner/restoration/workspace fullscreen/not tiled/missing clip/no owner; nested clip inheritance (unit only)");
}
int main(int argc,char **argv){if(argc==2&&strcmp(argv[1],"--allocation-unavailable")==0){struct wlr_scene_tree tree,prior;init_node(&tree.node,WLR_SCENE_NODE_TREE,NULL,0,0);init_node(&prior.node,WLR_SCENE_NODE_TREE,NULL,0,0);struct wlr_box b={0,0,10,10};wlr_scene_tree_set_clip(&prior,&b);assert(allocations==1&&clip_count()==1&&wl_list_length(&prior.node.events.destroy.listener_list)==1);allocation_unavailable=true;puts("INJECTION prior sidecar succeeded; next sidecar calloc returns NULL; expecting experimental abort");fflush(stdout);wlr_scene_tree_set_clip(&tree,&b);return 99;}lifecycle();popups();return 0;}
