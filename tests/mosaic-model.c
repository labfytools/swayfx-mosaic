#include <assert.h>
#include <stddef.h>
#include "sway/tree/mosaic.h"

// Distinct addresses stand for containers; the model must never dereference
// them or infer geometry from their identity.
static int a, b, c, d, x, f;
#define CON(v) ((struct sway_container *)&(v))

int main(void) {
	list_t *tiling = create_list();
	assert(tiling);
	list_add(tiling, CON(a));
	list_add(tiling, CON(b));
	list_add(tiling, CON(c));
	list_add(tiling, CON(d));
	struct mosaic_workspace_state *state = mosaic_state_create(tiling);
	assert(state && state->rows->length == 1);
	struct mosaic_row *row0 = state->rows->items[0];
	assert(row0->children == tiling && !row0->owns_children);

	assert(mosaic_row_focus(row0, CON(a)));
	mosaic_row_insert_after_focus(row0, CON(x));
	assert(tiling->length == 5 && tiling->items[0] == CON(a) &&
		tiling->items[1] == CON(x) && tiling->items[2] == CON(b) &&
		tiling->items[3] == CON(c) && tiling->items[4] == CON(d));
	mosaic_row_remove(row0, CON(c));
	assert(tiling->length == 4 && tiling->items[3] == CON(d));
	assert(mosaic_row_focus(row0, CON(b)));
	assert(tiling->items[0] == CON(a) && tiling->items[1] == CON(x));
	assert(mosaic_row_set_scroll(row0, 1200));
	assert(!mosaic_row_set_scroll(row0, -1));
	assert(tiling->items[2] == CON(b));
	assert(mosaic_row_max_scroll(row0, 1280, 0) == 1280);
	mosaic_row_clamp_scroll(row0, 1280, 0);
	assert(row0->state.scroll_x == 1200);
	assert(mosaic_row_max_scroll(row0, 2560, 0) == 0);
	// Clamping the camera does not change the borrowed Sway tiling order.
	assert(tiling->items[2] == CON(b));

	struct mosaic_row *row1 = mosaic_state_add_row(state);
	assert(row1 && row1->owns_children);
	list_add(row1->children, CON(f));
	assert(mosaic_row_max_scroll(row1, 300, 0) == 340);
	assert(mosaic_row_focus(row1, CON(f)));
	assert(mosaic_row_set_scroll(row1, 400));
	assert(mosaic_state_select_row(state, 1));
	assert(mosaic_state_select_row(state, 0));
	assert(row0->state.scroll_x == 1200 && row0->state.focused == CON(b));
	assert(row1->state.scroll_x == 400 && row1->state.focused == CON(f));
	mosaic_row_remove(row0, CON(b));
	assert(row0->state.focused == NULL);
	assert(!mosaic_state_select_row(state, 2));
	mosaic_state_destroy(state);
	assert(tiling->length == 3); // Borrowed Sway list survives state destruction.
	list_free(tiling);
	return 0;
}
