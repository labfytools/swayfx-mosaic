#ifndef _SWAY_MOSAIC_H
#define _SWAY_MOSAIC_H

#include <stdbool.h>
#include "list.h"

struct sway_container;

// CONTRACT: children are ordered Sway tiling containers; scroll_x is a
// logical canvas coordinate, independent of focus and rendered geometry.
struct mosaic_row_state {
	double scroll_x;
	// STEP20B temporary sizing policy. Zero selects the current 640 px
	// minimum; this is not a stable Mosaic layout API.
	int minimum_cell_width;
	struct sway_container *focused;
};

struct mosaic_row {
	list_t *children;
	bool owns_children;
	struct mosaic_row_state state;
};

struct mosaic_workspace_state {
	list_t *rows; // struct mosaic_row; owns rows, never their containers.
	int active_row;
};

// The first row may borrow workspace->tiling. The caller keeps that list alive
// until mosaic_state_destroy; later rows own only their lists, not children.
// NULL input/allocation failure returns NULL. Destroy accepts NULL.
struct mosaic_workspace_state *mosaic_state_create(list_t *first_children);
void mosaic_state_destroy(struct mosaic_workspace_state *state);
// Model operation only: wiring another row into Sway's tree and scene is later
// work. NULL/allocation failure returns NULL; child ownership stays with Sway.
struct mosaic_row *mosaic_state_add_row(struct mosaic_workspace_state *state);
// Rejects an invalid row index without changing active_row.
bool mosaic_state_select_row(struct mosaic_workspace_state *state, int index);
// Insertion/removal must occur from a Sway tree mutation path, which also
// maintains parent/workspace pointers, representation and transaction dirtiness.
int mosaic_row_insertion_index(const struct mosaic_row *row);
void mosaic_row_insert_after_focus(struct mosaic_row *row,
		struct sway_container *child);
void mosaic_row_remove(struct mosaic_row *row, struct sway_container *child);
// Rejects a child not present in this row, preserving the last valid focus.
bool mosaic_row_focus(struct mosaic_row *row, struct sway_container *child);
// Rejects negative/NaN/infinite logical positions without changing the row.
bool mosaic_row_set_scroll(struct mosaic_row *row, double scroll_x);
// Clamp the logical camera to the currently arranged canvas. The viewport and
// row contents remain owned by Sway; this helper never mutates child order.
int mosaic_row_max_scroll(const struct mosaic_row *row, int viewport_width,
		int gaps);
void mosaic_row_clamp_scroll(struct mosaic_row *row, int viewport_width,
		int gaps);

#endif
