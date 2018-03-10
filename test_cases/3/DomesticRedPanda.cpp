#include "DomesticRedPanda.h"
#include <stdlib.h>
#include <stdio.h>

DomesticRedPanda::DomesticRedPanda(int num_teeth) :
        RedPanda(num_teeth) {
}

DomesticRedPanda::~DomesticRedPanda() {
}

void DomesticRedPanda::Feed(int pounds_of_food) {
    printf("I am a domestic red with %d teeth and I ate %d pounds of catfood :)\n",
           m_num_teeth, pounds_of_food);
    malloc(9);
}
