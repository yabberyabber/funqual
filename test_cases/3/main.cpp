#include "funqual.h"
#include "Panda.h"
#include "RedPanda.h"
#include "TrashPanda.h"

#include <stdlib.h>

void *malloc(size_t size) QTAG(dynamic_memory);

void FeedPanda() {
    Panda *panda = new RedPanda(18);

    panda->Feed(7);
}

void FeedRaccoon() {
    TrashPanda *raccoon = new TrashPanda(19);

    raccoon->Feed(17);
}

int main(void) QTAG(static_memory) {
    FeedPanda();
    FeedRaccoon();

    return 0;
}
