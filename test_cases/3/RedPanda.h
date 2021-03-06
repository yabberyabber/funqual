#pragma once

#include "Panda.h"
#include "funqual.h"

class RedPanda : public Panda {
public:
    RedPanda(int num_teeth);
    virtual ~RedPanda();

    virtual void Feed(int pounds_of_food) QTAG(static_memory) override;
};
