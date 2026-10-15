// Reduced Sway/protocol adapters for the exact input_popup_set_focus body.
// No protocol/grab or real compositor focus/damage claim.
struct wlr_surface {struct {struct wl_signal unmap;}events;};
struct wlr_layer_surface_v1 {struct wlr_surface *surface;void *data;struct wlr_output *output;};
struct wlr_session_lock_surface_v1 {struct wlr_surface *surface;void *data;};
struct sway_container;
struct sway_view {struct wlr_scene_tree *scene_tree;struct {struct wl_signal unmap;}events;struct sway_container *container;};
struct sway_popup_desc {struct wlr_scene_node *relative;struct sway_view *view;};
struct sway_input_popup {struct wl_listener focused_surface_unmap;struct wlr_scene_tree *scene_tree;struct sway_popup_desc desc;struct wlr_output *fixed_output;};
struct sway_layer_surface {struct {struct wlr_scene_tree *tree;} *scene;struct wlr_layer_surface_v1 *layer_surface;};
static struct sway_view *focused_view;
static bool descriptor_live,descriptor_failure;
static unsigned constraints;
#define SWAY_SCENE_DESC_POPUP 1
#define SWAY_DEBUG 1
#define sway_log(level, ...) ((void)(level))
static struct wlr_layer_surface_v1 *wlr_layer_surface_v1_try_from_wlr_surface(struct wlr_surface *s){(void)s;return NULL;}
static struct wlr_session_lock_surface_v1 *wlr_session_lock_surface_v1_try_from_wlr_surface(struct wlr_surface *s){(void)s;return NULL;}
static struct sway_view *view_from_wlr_surface(struct wlr_surface *s){(void)s;return focused_view;}
static void scene_descriptor_destroy(struct wlr_scene_node *n,int type){(void)n;(void)type;descriptor_live=false;}
static bool scene_descriptor_assign(struct wlr_scene_node *n,int type,void *d){(void)n;(void)type;(void)d;if(descriptor_failure)return false;descriptor_live=true;return true;}
static void constrain_popup(struct sway_input_popup *p){(void)p;constraints++;}
#include "ime.inc"
static void ime_tests(struct wlr_scene_tree *root) {
    watched=NULL;fail_reservation=0;
    struct sway_view view={.scene_tree=wlr_scene_tree_create(root)};assert(view.scene_tree);wl_signal_init(&view.events.unmap);focused_view=&view;
    struct sway_input_popup popup={.scene_tree=wlr_scene_tree_create(root)};assert(popup.scene_tree);wl_list_init(&popup.focused_surface_unmap.link);
    struct wlr_surface surface={0};wl_signal_init(&surface.events.unmap);
    input_popup_set_focus(&popup,&surface);assert(popup.scene_tree->node.enabled);assert(popup.desc.relative);assert(descriptor_live);assert(wl_list_length(&view.events.unmap.listener_list)==1);
    fail_reservation=reservations+1;
    input_popup_set_focus(&popup,&surface);assert(!popup.scene_tree->node.enabled);assert(!popup.desc.relative&&!popup.desc.view&&!popup.fixed_output);assert(!descriptor_live);assert(wl_list_empty(&view.events.unmap.listener_list));assert(wl_list_empty(&view.scene_tree->children));
    // A failed refocus can be retried; only complete admission re-enables.
    fail_reservation=0;input_popup_set_focus(&popup,&surface);assert(popup.scene_tree->node.enabled&&popup.desc.relative);assert(wl_list_length(&view.events.unmap.listener_list)==1);
    descriptor_failure=true;input_popup_set_focus(&popup,&surface);assert(!popup.scene_tree->node.enabled);assert(!popup.desc.relative&&!descriptor_live);assert(wl_list_empty(&view.events.unmap.listener_list));assert(wl_list_empty(&view.scene_tree->children));
    descriptor_failure=false;input_popup_set_focus(&popup,&surface);assert(popup.scene_tree->node.enabled);
    input_popup_set_focus(&popup,NULL);assert(!popup.scene_tree->node.enabled&&!popup.desc.relative&&!descriptor_live);assert(wl_list_empty(&view.events.unmap.listener_list));
    wlr_scene_node_destroy(&popup.scene_tree->node);wlr_scene_node_destroy(&view.scene_tree->node);focused_view=NULL;assert(!count_clips());
}
