from core import lex, run, check, rewrite
from stdlib import builtins
from utils import ansi

stack = list()
types = list()
errors = list()
while True:
    for error in errors: print(f'{ansi('Error', 91)}{ansi(':', 90)} {error[1]}')
    code = input(f"{ansi('🧶', 35)}{ansi('(', 90)}{len(stack)}{ansi(')', 90)} ")
    while code.count('(') > code.count(')') and code.count('{') > code.count('}'):
        code += input(ansi(f'🧶{len(str(len(stack)))*'.'}.. ', 90))
    tokens = lex(code, errors)
    if len(errors) != 0: continue
    tokens = rewrite(tokens, errors)
    if len(errors) != 0: continue
    check(tokens, builtins, types, errors)
    if len(errors) != 0: continue
    run(tokens, builtins, stack)
