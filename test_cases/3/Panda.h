#pragma once

#include "funqual.h"

class Panda {
public:
    Panda(int num_teeth);
    virtual ~Panda();

    virtual void Feed(int pounds_of_food) QTAG(static_memory);

    Panda operator + (Panda const &panda);
protected:
    const int m_num_teeth;
};
