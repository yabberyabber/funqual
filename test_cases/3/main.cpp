#include "funqual.h"
#include "Panda.h"
#include "RedPanda.h"
#include "TrashPanda.h"

#include <stdlib.h>

void *malloc(size_t size) QTAG(dynamic_memory);

Panda g_panda(3);

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

    Panda babyPanda = Panda(4) + Panda(6);
    babyPanda.Feed(7);

    return 0;
}
