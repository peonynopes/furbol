# Furbol
Furbol is a statically-typed, stack-based
language designed to be simple yet powerful. It takes
heavy inspiration from [Kitten](https://kittenlang.org/).
Furbol is currently implemented as an interpreter with
an interactive "dialog" (REPL). It is intended as a
systems language and thus has a planned LLVM, C, Forth
or other possible backends, however at the current stage
no guarantees can be made.

## Installing
Currently, the only available version of Furbol is
written in Python, however a self-hosted version is
planned.

The only way to install furbol is to first [install
Python 3.13.7](https://python.org) (unless an
installation is already available) and then to clone
this repository with:

```shell
git clone https://github.com/peonynopes/furbol.git
```
To get an interactive Furbol dialog run the Python file
named `./furbol.py`

## Syntax
The Furbol syntax is close to trivial however there
are a few caveats.

### Function application
Due to being concatenative application is the default.

```fur
'meow' say
```
This "reverse" function calling syntax may be
confusing to new users or not fitting in all contexts,
therefore Furbol uses a Smalltalk like `:` symbol that
can be used to fully or partially reverse the way
functions are called.

```fur
say: 'meow'
1 add: 2
add: 1 2
add: 1 2; add: 3 
```

#### Rewriting details
There is a rewriting step during which some of the code
is rewritten into a fully concatenative form.
`:` is a keyword that triggers such rewriting. The word
before the colon is taken and pushed all the way towards
the end of the line (inside braces and parentheses the
closing brace or bracket is treated as the end of line)
or until a semicolon. This allows for chaining multiple
functions even when one or many of them are using `:`.

### Operators
Operators use a similar style of rewriting to the colon
symbol however they trigger the rewriting by themselves
and have the concept of precedence. Operators take an
entire expression on their right hand side meaning they
skip over consecutive words but not consecutive constants
allowing for expressions like.

```fur
(n - 1) fib + (n - 2) fib
```
There is currently no complete list of operators as they
are still being implemented however Furbol aims to have
parity with [Tau](https://github.com/tau-language/tau-tmp-spec/blob/main/operators.md) operator wise.

