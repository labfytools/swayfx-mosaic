/* EXPERIMENTAL synthetic branch model, not a wlroots backend test.
 * WHY: rejected commits and output destruction have no safe, controlled
 * trigger in the fixed headless matrix. Model only extra probe ownership.
 * CONTRACT: one extra lock must be released exactly once on each branch.
 * INVARIANT: clear the output slot before invoking the unlock callback. */
#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

struct fake_buffer {
    unsigned locks;
    unsigned unlocks;
};
struct fake_hold {
    struct fake_buffer *buffer;
    bool timer;
    unsigned output_id;
};

static void unlock(struct fake_buffer *buffer) {
    assert(buffer->locks == buffer->unlocks + 1);
    ++buffer->unlocks;
}

static void release_hold(struct fake_hold *hold) {
    if (!hold || !hold->buffer) return;
    struct fake_buffer *buffer = hold->buffer;
    memset(hold, 0, sizeof(*hold));
    unlock(buffer);
}

int main(void) {
    struct fake_buffer rejected = {.locks = 1};
    /* output.c direct rejection branch: the slot was never installed. */
    unlock(&rejected);
    assert(rejected.unlocks == 1);

    struct fake_buffer destroyed = {.locks = 1};
    struct fake_hold hold = {.buffer = &destroyed, .timer = true, .output_id = 1};
    /* output.c begin_destroy branch and a late idempotent release request. */
    release_hold(&hold);
    release_hold(&hold);
    assert(destroyed.unlocks == 1 && hold.buffer == NULL && !hold.timer);
    puts("SYNTHETIC_REJECT_AND_DESTROY=PASS (no backend triggered)");
    return 0;
}
