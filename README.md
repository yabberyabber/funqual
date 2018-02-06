# Funqual - User defined static call tree constraints in C++

Funqual is a tool that examines standard C++17 code and checks for user-defined constraints to the call-tree.  Think of it as a type system for function calls.  You can't add an int and a string therefore you shouldn't be able to call a blocking function from a nonblocking function.

This tool is currently an early prototype.  In the next few weeks it should transition from being a prototype that works for a few specific cases to a useful tool that works in the general case and which could be deployed on any C++ codebase.  

## Usage

Depends on python's clang library.

`python parse.py header.hpp -t ext_tags.qtag`
