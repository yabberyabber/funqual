# Funqual - User defined static call tree constraints in C++

Funqual is a tool that examines standard C++17 code and checks for user-defined constraints to the call-tree.  Think of it as a type system for function calls.  You can't add an int and a string therefore you shouldn't be able to call a blocking function from a nonblocking function.

This tool is currently an early prototype.  In the next few weeks it should transition from being a prototype that works for a few specific cases to a useful tool that works in the general case and which could be deployed on any C++ codebase.  

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
