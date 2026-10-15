// Reduced current-state Sway adapters; no transactions, renderer or protocol run.
#define L_MOSAIC 99
#define SWAY_INFO 1
struct list_t {int length;void **items;};
static int list_find(struct list_t *list,void *item){for(int i=0;i<list->length;i++)if(list->items[i]==item)return i;return -1;}
struct side_gaps {int left,right,top,bottom;};
struct mosaic_row {struct {double scroll_x;}state;};
struct mosaic_workspace {struct list_t *rows;};
struct sway_workspace;
struct sway_output {struct {struct sway_workspace *active_workspace;}current;int lx,ly,width,height;};
struct sway_workspace {struct {int layout;struct list_t *tiling;struct sway_output *output;}current;struct mosaic_workspace *mosaic;struct {struct wlr_scene_tree *tiling;}layers;};
struct sway_container {struct {struct sway_workspace *workspace;struct sway_container *parent;int fullscreen_mode;}current;struct wlr_scene_tree *scene_tree;struct {int current_width,current_height;}animation_state;};
#include "transaction.inc"
static void transaction_tests(struct wlr_scene_tree *root) {
    struct wlr_scene_tree *tiling=wlr_scene_tree_create(root),*popup=wlr_scene_tree_create(root);assert(tiling&&popup);
    struct sway_container parent={.scene_tree=wlr_scene_tree_create(tiling)},con={.scene_tree=wlr_scene_tree_create(parent.scene_tree),.animation_state={100,100}};
    con.current.parent=&parent;
    void *owners[]={&parent};struct list_t ownerlist={1,owners};
    struct mosaic_row row={0};void *rows[]={&row};struct list_t rowlist={1,rows};struct mosaic_workspace mosaic={&rowlist};
    struct sway_workspace ws={.current={.layout=L_MOSAIC,.tiling=&ownerlist},.mosaic=&mosaic,.layers={tiling}};
    struct sway_output output={.current={&ws},.width=800,.height=600};ws.current.output=&output;con.current.workspace=&ws;parent.current.workspace=&ws;
    struct wlr_box area={0,0,800,600};struct side_gaps gaps={0};struct wlr_box out;
    probe_workspace_clip(&ws,&area,&gaps);assert(wlr_scene_tree_get_clip(tiling,&out)&&out.width==800);
    struct sway_view view={.container=&con};struct sway_popup_desc desc={.view=&view};
    probe_clip_popup(&popup->node,&desc);assert(wlr_scene_tree_get_clip(popup,&out)&&out.width==800);
    assert(scene_node_point_inside_clip(&popup->node,50,50));
    con.scene_tree->node.x=1000;probe_clip_popup(&popup->node,&desc);assert(wlr_scene_tree_get_clip(popup,&out)&&out.width==0);assert(!scene_node_point_inside_clip(&popup->node,50,50));
    con.scene_tree->node.x=0;probe_clip_popup(&popup->node,&desc);assert(wlr_scene_tree_get_clip(popup,&out)&&out.width==800);
    struct wlr_scene_tree *nested=wlr_scene_tree_create(popup);assert(scene_node_point_inside_clip(&nested->node,50,50));assert(!scene_node_point_inside_clip(&nested->node,900,50));
    // Non-leaf CURRENT fullscreen ancestor clears exemption, independent of ws.
    parent.current.fullscreen_mode=1;probe_clip_popup(&popup->node,&desc);assert(!wlr_scene_tree_get_clip(popup,&out));parent.current.fullscreen_mode=0;
    probe_clip_popup(&popup->node,&desc);assert(wlr_scene_tree_get_clip(popup,&out));
    ws.current.layout=0;probe_workspace_clip(&ws,&area,&gaps);probe_clip_popup(&popup->node,&desc);assert(!wlr_scene_tree_get_clip(tiling,&out)&&!wlr_scene_tree_get_clip(popup,&out));
    ws.current.layout=L_MOSAIC;
    double extremes[]={NAN,INFINITY,-INFINITY,1e300,-1e300};
    for(unsigned i=0;i<sizeof(extremes)/sizeof(*extremes);i++) {row.state.scroll_x=extremes[i];probe_workspace_clip(&ws,&area,&gaps);assert(wlr_scene_tree_get_clip(tiling,&out)&&out.width==0);(void)workspace_tiling_scene_x(&ws,&area,&gaps);}
    row.state.scroll_x=42.9;probe_workspace_clip(&ws,&area,&gaps);assert(wlr_scene_tree_get_clip(tiling,&out)&&out.x==42);assert(workspace_tiling_scene_x(&ws,&area,&gaps)==-42);
    // This helper is used by the full-source fading branch; no engine fading claim.
    row.state.scroll_x=100;probe_workspace_clip(&ws,&area,&gaps);assert(wlr_scene_tree_get_clip(tiling,&out)&&out.x==100);
    wlr_scene_node_destroy(&popup->node);wlr_scene_node_destroy(&tiling->node);assert(!count_clips());
}
