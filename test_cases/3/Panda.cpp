#include "Panda.h"
#include <stdio.h>
#include <stdlib.h>

Panda::Panda(int num_teeth) :
        m_num_teeth(num_teeth) {
}

Panda::~Panda() {
}

void Panda::Feed(int pounds_of_food) {
    printf("I am a panda with %d teeth and I ate %d pounds of food :)\n",
           m_num_teeth, pounds_of_food);
}

Panda Panda::operator + (Panda const &panda) {
    malloc(4);
    return Panda((m_num_teeth + panda.m_num_teeth) / 2);
}
