/* WHY: a deterministic H2 reference cannot contain Kitty's blinking cursor.
 * CONTRACT: use the same real XDG configure/ACK loop with fixed opaque SHM.
 * INVARIANT: once configured and stable, this client changes no pixels. */
#define STATIC_REFERENCE 1
#include "saved-client.c"
