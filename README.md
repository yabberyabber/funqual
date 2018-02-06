# Funqual - User defined static call tree constraints in C++

Funqual is a tool that examines standard C++17 code and checks for user-defined constraints to the call-tree.  Think of it as a type system for function calls.  You can't add an int and a string therefore you shouldn't be able to call a blocking function from a nonblocking function.
