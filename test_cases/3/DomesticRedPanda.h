#pragma once

#include "RedPanda.h"

class DomesticRedPanda : public RedPanda {
public:
    DomesticRedPanda(int num_teeth);
    virtual ~DomesticRedPanda();

    virtual void Feed(int pounds_of_food) override;
};
