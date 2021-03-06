#define QTAG(TAG) __attribute__((annotate("funqual::" #TAG)))
#define QTAG_IND(TAG) __attribute__((annotate("funqual_indirect::" #TAG)))

extern int printf(const char *__restrict __format, ...) QTAG(io);

int something_that_calls_printf() QTAG(goopy) QTAG(oopsy) {
    return printf("ohh no!\n");
}

int something_that_doesnt_call_printf() {
    // yay!
    return 0;
}

void intermediate() {
    int  QTAG(oopsy) QTAG_IND(io) (*func)() = something_that_doesnt_call_printf, bar;

    func = something_that_calls_printf;

    func();
}

int main(void) QTAG(no_io) {
    intermediate();
    
    return 0;
}
