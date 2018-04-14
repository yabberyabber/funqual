#define QTAG(TAG) __attribute__((annotate("funqual::" #TAG)))
#define QTAG_INDIRECT(TAG) __attribute__((annotate("funqual::" #TAG)))

extern int printf(const char *__restrict __format, ...) QTAG(io);

int something_that_calls_printf() {
    return printf("ohh no!\n");
}

int something_that_doesnt_call_printf() {
    // yay!
    return 0;
}

int main(void) QTAG(no_io) {
    int QTAG_INDIRECT(goopy) (*func)() = something_that_doesnt_call_printf;

    func = something_that_calls_printf;

    func();
    
    return 0;
}
