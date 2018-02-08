#include <stdio.h>

#define FUNQUAL_TAG(TAG) __attribute__((annotate("funqual::" #TAG)))

struct Oops {
};

struct Wowza {
    virtual ~Wowza() = default;
    virtual void doSomething(int i = 0) FUNQUAL_TAG(marvin) = 0;
    void UpsideDown() FUNQUAL_TAG(realtime) FUNQUAL_TAG(preemptive);
};

void Wowza::UpsideDown() {
    printf("oops!");
    return;
}

int getTime(FUNQUAL_TAG(blocking)const char *j) {
    int i FUNQUAL_TAG(blocking) = 9;
    int z = getTime("");
    return 1141;
}

void doSomething() FUNQUAL_TAG(blocking) {
    while (true) {
        getTime("");
    }
    getTime("");
}

void call_printf() {
    printf("This call was a sneaky sneaky beast!");
}

void do_something_that_calls_printf() {
    call_printf();
    printf("");
}

void foo() FUNQUAL_TAG(preemptive) {
    call_printf();
    printf("");
    do_something_that_calls_printf();
}
