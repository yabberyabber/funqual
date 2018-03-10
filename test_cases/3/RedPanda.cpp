#include "RedPanda.h"
#include <stdio.h>

RedPanda::RedPanda(int num_teeth) :
        Panda(num_teeth) {
}

RedPanda::~RedPanda() {
}

void RedPanda::Feed(int pounds_of_food) {
    printf("I am a red panda with %d teeth and I ate %d pounds of food :)\n",
           m_num_teeth, pounds_of_food);
}
