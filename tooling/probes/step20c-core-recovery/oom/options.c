#define main historical_main
#include "lifecycle.c"
#undef main
extern unsigned fail_at,publications;
#ifdef MODE_C
struct wlr_scene_tree *wlr_scene_tree_create(struct wlr_scene_tree *);
#endif
static void oom(unsigned nth){
 struct wlr_scene_tree root;init_node(&root.node,WLR_SCENE_NODE_TREE,NULL,0,0);
 struct wlr_box b={0,0,10,10},out;
#ifdef MODE_C
 unsigned before=publications;fail_at=allocations+nth;
 struct wlr_scene_tree *t=wlr_scene_tree_create(&root);
 assert(!t && publications==before && clip_count()==0);
 assert(wl_list_empty(&root.node.events.destroy.listener_list));
 printf("PASS C reservation allocation %u: NULL before publication/listener; no exposed tree\n",nth);
#else
 struct wlr_scene_tree prior;init_node(&prior.node,WLR_SCENE_NODE_TREE,NULL,0,0);
 if(nth==2)wlr_scene_tree_set_clip(&prior,&b);
 fail_at=allocations+1;
#ifdef MODE_B
 unsigned old_updates=old_region_updates;
 assert(!wlr_scene_tree_set_clip(&root,&b));assert(!root.node.enabled);assert(old_region_updates==old_updates+1);
 struct wlr_scene_buffer leaf={.point_accepts_input=input};init_node(&leaf.node,WLR_SCENE_NODE_BUFFER,&root,0,0);
 assert(!hit(&leaf.node,1,1) && input_calls==0);
 root.node.parent=&prior;assert(!hit(&leaf.node,1,1));root.node.parent=NULL;assert(!hit(&leaf.node,1,1));
 assert(!wlr_scene_tree_get_clip(&root,&out));
 fail_at=0;assert(wlr_scene_tree_set_clip(&root,&b));assert(!root.node.enabled);
 assert(wlr_scene_tree_set_clip(&root,NULL));assert(!root.node.enabled);
 destroy(&root);destroy(&prior);assert(clip_count()==0);
 printf("PASS B allocation %u: false masks ancestor before hit; recovery/NULL do not enable\n",nth);
#else
 puts("EXPECT SIGABRT core_limit=0");fflush(stdout);wlr_scene_tree_set_clip(&root,&b);exit(99);
#endif
#endif
}
#ifdef MODE_C
static void reserved(void){
 struct wlr_scene_tree root;init_node(&root.node,WLR_SCENE_NODE_TREE,NULL,0,0);
 struct wlr_scene_tree *p=wlr_scene_tree_create(&root),*c=wlr_scene_tree_create(p),*other=wlr_scene_tree_create(&root);assert(p&&c&&other);
 struct wlr_scene_buffer leaf={.point_accepts_input=input};init_node(&leaf.node,WLR_SCENE_NODE_BUFFER,c,0,0);
 struct wlr_box b={0,0,10,10},out;unsigned n=allocations;allocation_unavailable=true;
 wlr_scene_tree_set_clip(p,NULL);assert(!wlr_scene_tree_get_clip(p,&out));
 wlr_scene_tree_set_clip(p,&b);assert(hit(&leaf.node,1,1)&&!hit(&leaf.node,11,1));
 b=(struct wlr_box){0};wlr_scene_tree_set_clip(c,&b);assert(!hit(&leaf.node,1,1));
 wlr_scene_tree_set_clip(c,NULL);assert(hit(&leaf.node,1,1));
 // WHY: clips follow current parent pointers, not stale ownership snapshots.
 // CONTRACT: this direct fixture reparent exercises exact ancestry walkers only.
 // INVARIANT: no claim is made about native reparent damage or scene children.
 c->node.parent=other;assert(hit(&leaf.node,11,1));c->node.parent=p;assert(!hit(&leaf.node,11,1));
 wlr_scene_tree_set_clip(p,NULL);wlr_scene_tree_set_clip(p,&b);assert(!hit(&leaf.node,1,1));assert(allocations==n);
 destroy(p);destroy(c);destroy(other);free(p);free(c);free(other);assert(clip_count()==0);
 puts("PASS C NULL/clip/zero/removal/reinstall/inherited hit/reparent/parent-before-child destroy; zero setter allocations");
}
#endif
#ifdef MODE_B
static void admission(void){
 struct wlr_scene_tree tree;init_node(&tree.node,WLR_SCENE_NODE_TREE,NULL,0,0);
 struct sway_workspace ws={.current={.layout=L_MOSAIC},.mosaic=&ws,.layers={&tree}};
 struct sway_workspace *child=&ws;
 struct wlr_box box={0,0,10,10};
 fail_at=allocations+1;assert(!wlr_scene_tree_set_clip(&tree,&box));assert(!tree.node.enabled);
 // Exact statement from the private fading-out branch, plus exact helper body.
 #include "fading.inc"
 assert(!tree.node.enabled);
 fail_at=0;assert(wlr_scene_tree_set_clip(&tree,&box));assert(!tree.node.enabled);
 probe_clip_enable_tiling(&ws,false);assert(!tree.node.enabled);
 #include "fading.inc"
 assert(tree.node.enabled);
 assert(wlr_scene_tree_set_clip(&tree,NULL));
 #include "fading.inc"
 assert(!tree.node.enabled);
 ws.current.layout=L_STANDARD;
 #include "fading.inc"
 assert(tree.node.enabled);
 probe_clip_enable_tiling(&ws,false);assert(!tree.node.enabled);
 destroy(&tree);assert(clip_count()==0);
 puts("PASS B exact fading admission: OOM cannot re-enable; desired false preserved; repaired clip/standard admit only explicit desired true");
}
#endif
int main(int argc,char **argv){if(argc==2){oom((unsigned)atoi(argv[1]));return 0;}
#ifdef MODE_C
 reserved();allocation_unavailable=false;popups();
#else
 lifecycle();popups();
#ifdef MODE_B
 admission();
#endif
#endif
 return 0;}
