#include <math.h>
#include <limits.h>
#include <stdint.h>
#include <stdlib.h>
#include "sway/tree/mosaic.h"

static struct mosaic_row *row_create(list_t *children, bool owns_children) {
	struct mosaic_row *row = calloc(1, sizeof(*row));
	if (!row) {
		return NULL;
	}
	row->children = children;
	row->owns_children = owns_children;
	return row;
}

struct mosaic_workspace_state *mosaic_state_create(list_t *first_children) {
	if (!first_children) {
		return NULL;
	}
	struct mosaic_workspace_state *state = calloc(1, sizeof(*state));
	if (!state) {
		return NULL;
	}
	state->rows = create_list();
	if (!state->rows) {
		free(state);
		return NULL;
	}
	struct mosaic_row *row = row_create(first_children, false);
	if (!row) {
		list_free(state->rows);
		free(state);
		return NULL;
	}
	list_add(state->rows, row);
	return state;
}

void mosaic_state_destroy(struct mosaic_workspace_state *state) {
	if (!state) {
		return;
	}
	for (int i = 0; i < state->rows->length; ++i) {
		struct mosaic_row *row = state->rows->items[i];
		if (row->owns_children) {
			list_free(row->children);
		}
		free(row);
	}
	list_free(state->rows);
	free(state);
}

struct mosaic_row *mosaic_state_add_row(struct mosaic_workspace_state *state) {
	if (!state) {
		return NULL;
	}
	list_t *children = create_list();
	if (!children) {
		return NULL;
	}
	struct mosaic_row *row = row_create(children, true);
	if (!row) {
		list_free(children);
		return NULL;
	}
	list_add(state->rows, row);
	return row;
}

bool mosaic_state_select_row(struct mosaic_workspace_state *state, int index) {
	if (!state || index < 0 || index >= state->rows->length) {
		return false;
	}
	state->active_row = index;
	return true;
}

int mosaic_row_insertion_index(const struct mosaic_row *row) {
	if (!row || !row->children) {
		return 0;
	}
	int index = list_find(row->children, row->state.focused);
	return index < 0 ? row->children->length : index + 1;
}

void mosaic_row_insert_after_focus(struct mosaic_row *row,
		struct sway_container *child) {
	if (row && child) {
		list_insert(row->children, mosaic_row_insertion_index(row), child);
	}
}

void mosaic_row_remove(struct mosaic_row *row, struct sway_container *child) {
	if (!row || !child) {
		return;
	}
	int index = list_find(row->children, child);
	if (index >= 0) {
		list_del(row->children, index);
	}
	// INVARIANT: no row retains focus on a detached or destroyed container.
	if (row->state.focused == child) {
		row->state.focused = NULL;
	}
}

bool mosaic_row_focus(struct mosaic_row *row, struct sway_container *child) {
	if (!row || (child && list_find(row->children, child) < 0)) {
		return false;
	}
	row->state.focused = child;
	return true;
}

bool mosaic_row_set_scroll(struct mosaic_row *row, double scroll_x) {
	if (!row || !isfinite(scroll_x) || scroll_x < 0) {
		return false;
	}
	row->state.scroll_x = scroll_x;
	return true;
}

int mosaic_row_max_scroll(const struct mosaic_row *row, int viewport_width,
		int gaps) {
	if (!row || !row->children || viewport_width <= 0 ||
			row->children->length == 0) {
		return 0;
	}
	int count = row->children->length;
	int cell = row->state.minimum_cell_width > 0 ?
		row->state.minimum_cell_width : 640;
	if (gaps < 0) {
		gaps = 0;
	}
	int64_t occupied_gaps = (int64_t)(count - 1) * gaps;
	int64_t fitting = ((int64_t)viewport_width - occupied_gaps) / count;
	if (fitting > cell) {
		cell = fitting > INT_MAX ? INT_MAX : (int)fitting;
	}
	int64_t overflow = (int64_t)count * cell + occupied_gaps - viewport_width;
	return overflow <= 0 ? 0 : overflow > INT_MAX ? INT_MAX : (int)overflow;
}

void mosaic_row_clamp_scroll(struct mosaic_row *row, int viewport_width,
		int gaps) {
	if (!row) {
		return;
	}
	int maximum = mosaic_row_max_scroll(row, viewport_width, gaps);
	if (row->state.scroll_x > maximum) {
		row->state.scroll_x = maximum;
	}
}
