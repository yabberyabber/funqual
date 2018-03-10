#include "TrashPanda.h"
#include <stdio.h>

TrashPanda::TrashPanda(int num_teeth) :
        Panda(num_teeth) {
}

TrashPanda::~TrashPanda() {
}

void TrashPanda::Feed(int pounds_of_food) {
    printf("I am a raccoon with %d teeth and I ate %d pounds of food :)\n",
           m_num_teeth, pounds_of_food);
}
