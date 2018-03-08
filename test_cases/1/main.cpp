#include "alt.h"

#define QTAG(TAG) __attribute__((annotate("funqual::" #TAG)))

void do_stuff() QTAG(static_memory) {
    save_the_pandas();
}

int main(void) {
    do_stuff();
}
