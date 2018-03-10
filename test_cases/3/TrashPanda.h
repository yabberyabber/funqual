#pragma once

#include "Panda.h"

class TrashPanda : public Panda {
public:
    TrashPanda(int num_teeth);
    virtual ~TrashPanda();

    virtual void Feed(int pounds_of_food) override;
};
