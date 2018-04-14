#include <stdlib.h>
#include <stdio.h>

#include "alt.h"

static void stop_deforestation() {
    // TODO
}

static void increase_environment() {
    // TODO
}

static void stop_hunting(int num_hunters) {
    void *buff;
    buff = malloc(num_hunters * sizeof(long));
    printf("Allocated %p\n", buff);
    // TODO
}

int hunt_a_little_less() {
    void *buff = malloc(sizeof(short));
    return 9;
}

int save_the_pandas() {
    stop_deforestation();
    stop_hunting(9);
    increase_environment();
    return 0;
}
