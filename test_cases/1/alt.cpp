#include <stdlib.h>
#include <stdio.h>

#include "alt.h"

void stop_deforestation() {
    // TODO
}

void increase_environment() {
    // TODO
}

void stop_hunting(int num_hunters) {
    void *buff;
    buff = malloc(num_hunters * sizeof(long));
    printf("Allocated %p\n", buff);
    // TODO
}

int save_the_pandas() {
    stop_deforestation();
    stop_hunting(9);
    increase_environment();
    return 0;
}
