#include <stdio.h>
#include <stdlib.h>

#define QTAG(TAG) __attribute__((annotate("funqual::" #TAG)))

int printf(const char *__restrict __format, ...) QTAG(io);
void *malloc(size_t size) QTAG(dynamic_memory);

class Panda {
public:
    Panda() {
    }

    virtual ~Panda() {
    }

    virtual void Feed(int pounds_of_food) QTAG(somethingrather) {
        printf("I am a panda and I ate %d pounds of food :)\n",
               pounds_of_food);
    }
};

class RedPanda : public Panda {
public:
    RedPanda() {
    }

    virtual ~RedPanda() {
    }

    virtual void Feed(int pounds_of_food) override {
        printf("I am a red panda and I ate %d pounds of food :)\n",
               pounds_of_food);
        malloc( 5 );
    }
};

int main(void) QTAG(static_memory) {
    Panda *panda = new RedPanda();

    panda->Feed(9);
    
    return 0;
}
