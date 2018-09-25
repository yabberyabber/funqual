# Funqual - User defined static call tree constraints in C++

Funqual is a tool that examines standard C++17 code and checks for user-defined constraints to the call-tree.  Think of it as a type system for function calls.  You can't add an int and a string therefore you shouldn't be able to call a blocking function from a nonblocking function.

This tool introduces two ideas into your project:  the idea of function "qualified type" (is this function preemptive? nonreentrant? blocking? nonblocking? etc), and the idea of a "call tree constraint" (functions of type X can/cannot call functions of type Y).  Using these constructs, the programmer can statically assert that their program's call tree conform to whatever set of constraints they can think of.

Funqual has been successfully used to find issues in several small to medium sized projects.  Past use cases have been:
 - checking that non-reentrant functions are not called from signal handlers and other preemptive contexts
 - checking that syscalls are not called in high frequency control loops for a robotic controls library
 - checking that kernel startup code does not call functions associated with subsystems that aren't available at startup time

# Using

Function declarations can be annotated using any of the following syntaxes in source code:

```
#define QTAG(TAG) __attribute__((annotate("funqual::" #TAG)))

int foo(char *arg) QTAG(function_qualified_type) {
    ...
}

int QTAG(function_qualified_type) foo(char *arg);

class Bar {
    int foo(char *arg) QTAG(function_qualified_type);
};
```

Call tree constraints are added to a special rules file.  The rules file is passed to the funqual tool using the `-t` argument.  Below is an example of a rules file:

```
rule restrict_indirect_call preemptive non_reentrant
rule restrict_indirect_call nonblocking blocking
rule require_call realtime realtime
```

This file encodes the following rules:
 - functions with type `preemptive` may not call (whether direct or indirect) functions of type `non_reentrant`
 - functions with type `nonblocking` may not call (whether direct or indirect) functions of type `blocking`
 - functions wiht type `realtime` may only call functions of type `realtime`

In the future, a syntax may be added to encode call tree constraints in the program source without the need for an external rules file.  

## Example usage

You must have the clang module installed.  Install with the following: `python3 -m pip install clang`.

For a quick demo, run with the following command:

`python3 parse.py example/header.hpp -t example/ext_tags.qtag`

You should see output similar to the following:

```
Rule violation: `non_reentrant` function indirectly called from `preemptive` context
        Path:   example/header.hpp::foo() (41,6)
        -calls: example/header.hpp::call_printf() (32,6)
        -calls: example/header.hpp::(#include)::printf(const char *__restrict, ...) (362,12)

Rule violation: `non_reentrant` function indirectly called from `preemptive` context
        Path:   example/header.hpp::foo() (41,6)
        -calls: example/header.hpp::do_something_that_calls_printf() (36,6)
        -calls: example/header.hpp::call_printf() (32,6)
        -calls: example/header.hpp::(#include)::printf(const char *__restrict, ...) (362,12)

Rule violation: `non_reentrant` function indirectly called from `preemptive` context
        Path:   example/header.hpp::foo() (41,6)
        -calls: example/header.hpp::do_something_that_calls_printf() (36,6)
        -calls: example/header.hpp::(#include)::printf(const char *__restrict, ...) (362,12)

Rule violation: `non_reentrant` function indirectly called from `preemptive` context
        Path:   example/header.hpp::foo() (41,6)
        -calls: example/header.hpp::(#include)::printf(const char *__restrict, ...) (362,12)

Rule violation: `non_reentrant` function indirectly called from `preemptive` context
        Path:   example/header.hpp::Wowza::UpsideDown() (11,10)
        -calls: example/header.hpp::(#include)::printf(const char *__restrict, ...) (362,12)

Rule violation: `realtime` function calls a function that is not `realtime`
        Path:   example/header.hpp::Wowza::UpsideDown() (11,10)
        -calls: example/header.hpp::(#include)::printf(const char *__restrict, ...) (362,12)
```

# Building

This tool runs against libClang 3.8 with the patch supplied in the file pylibclang_get_overridden_cursors.patch.  I'm currently in the process of getting this patch added to libClang.  Fortunately, since these are only patches to the python bindings, you will not need to rebuild any part of libclang to get this working.  

# Future work

Since starting work on funqual I have finished grad school and started a full time job.  Updates from me will be sparse.  There is some low-hanging fruit as far as improvements go, though:
 - Dramatically improve speed by supporting incremental linting.  Users generally only change 3 or 4 files between lintings so why should we parse every file from scratch?
 - Merging patches into mainline libClang
 - Packaging into a .deb
