from __future__ import  annotations

from typing import Callable
from  types import FunctionType
from utils import ansi, format_types, Word, Keyword
import utils

type Pos = tuple[int, int]
type Loc = tuple[Pos, Pos]
type Err = tuple[Loc, str]

def peek(code: str) -> str | None:
    if len(code) == 0: return None
    return code[0]

def cont(result: str, code: str) -> tuple[str, str]: return result + code[0], code[1:]

NUMBERS = "0123456789"
def lex_number(code: str) -> type[int | float, str]:
    result = ""
    while peek(code) is not None and peek(code) in NUMBERS: result, code = cont(result, code)
    if peek(code) != '.': return int(result), code
    result, code = cont(result, code)
    while peek(code) in NUMBERS: result, code = cont(result, code)
    return float(result), code

def lex_string(code: str) -> type[str, str]:
    result = ""
    code = code[1:]
    while peek(code) is not None and peek(code) != "'":
        if peek(code) == '\\': code = code[1:]
        result, code = cont(result, code)
    if peek(code) == "'": return str(result), code[1:]
    return result, code

OPERATORS: dict[str, tuple[int, str]] = {
    '^': (1, 'exp'),
    '*': (2, 'mul'),
    '/': (2, 'div'),
    '%': (2, 'mod'),
    '+': (3, 'add'),
    '-': (3, 'sub'),
    #'<<': (4, 'lshift'),
    #'>>': (4, 'rshift'),
    #'&': (5, 'band'),
    #'|': (5, 'bor'),
    #'~': (5, 'bxor'),
}

SPECIAL = "():,{}" + ''.join(OPERATORS.keys())
def lex_word(code: str) -> type[Word, str]:
    result = ""
    while peek(code) is not None and ord(peek(code)) > 33 and peek(code) not in SPECIAL and peek(code) not in NUMBERS:
        result, code = cont(result, code)
    return Word(result), code

def lex(code: str, errors: list[Err]) -> list[utils.Token]:
    result, result_stack, code_stack = list(), list(), list()
    while len(code) > 0:
        match code[0]:
            case n if n in NUMBERS:
                value, code = lex_number(code)
                result.append(value)
            case "'":
                value, code = lex_string(code)
                result.append(value)
            case '{':
                code_stack.append(result)
                result = list()
                code = code[1:]
            case '}':
                code = code[1:]
                if len(code_stack) <= 0:
                    errors.append((((0, 0), (0, 0)), "Unopened brace!"))
                    continue
                expression = result
                result = code_stack.pop()
                result.append(([], [], expression))
            case '(':
                result_stack.append(result)
                result = list()
                code = code[1:]
            case ')':
                code = code[1:]
                if len(result_stack) <= 0:
                    errors.append((((0, 0), (0, 0)), "Unopened bracket!"))
                    continue
                expression = result
                result = result_stack.pop()
                result.append(expression)
            case '\n': result.append(Keyword('\n')); code = code[1:]
            case s if s in SPECIAL: result.append(Keyword(code[0])); code = code[1:]
            case s if ord(s) < 33: code = code[1:]
            case _:
                value, code = lex_word(code)
                result.append(value)
    if len(result_stack) > 0: errors.append((((0, 0), (0, 0)), "Unclosed bracket!"))
    if len(code_stack) > 0: errors.append((((0, 0), (0, 0)), "Unclosed brace!"))
    result.append(Keyword('\n')); return result

def rewrite(tokens: list[utils.Token], errors: list[Err]) -> list[utils.Token]:
    result = list()
    current_function: Word | None = None
    operator_stack = list()
    for token in tokens:
        match token:
            case Keyword(keyword):
                match keyword:
                    case ':': current_function = result.pop()
                    case ';':
                        if current_function is None: errors.append((((0, 0), (0, 0)), "Unexpected comma.")); continue
                        result.append(current_function); current_function = None
                    case '\n':
                        if current_function is not None: result.append(current_function); current_function = None
                    case o if o in OPERATORS.keys():
                        while len(operator_stack) > 0 and OPERATORS[operator_stack[-1]][0] <= OPERATORS[o][0]:
                            result.append(Word(OPERATORS[operator_stack.pop()][1]))
                        operator_stack.append(o)
            case list(expression):
                for expr in rewrite(expression, errors):
                    result.append(expr)
            case tuple(value):
                result.append(([], [], rewrite(value[2], errors)))
            case t:
                result.append(t)
                while len(operator_stack) > 0 and not isinstance(t, Word):
                    result.append(Word(OPERATORS[operator_stack.pop()][1]))
    while len(operator_stack) > 0: result.append(Word(OPERATORS[operator_stack.pop()][1]))
    if current_function is not None: result.append(current_function)
    return result

type CallableWord = tuple[list[type], list[type], Callable[[list[utils.Token]], None]]
def check(
        tokens: list[utils.Token],
        lexicon: dict[str, CallableWord],
        types: list[type],
        errors: list[Err],
        overpull: bool = False,
        overpulls: list[type] | None = None
    ) -> None:
    if overpulls is None: overpulls = list()
    for token in tokens:
        match token:
            case Word(word):
                if word not in lexicon.keys():
                    errors.append((((0,0), (0,0)), f"Word {ansi(word, 93)} is not in lexicon."))
                    return
                word_types = lexicon[word][0]
                if len(types) < len(word_types):
                    if overpull:
                        for i, t in enumerate(word_types):
                            if i >= len(types):
                                types.append(t)
                                overpulls.append(t)
                    else:
                        errors.append((((0,0), (0,0)),
                           f"{ansi(word, 93)} expected arguments {format_types(word_types)}, got {format_types(types)}"
                        ))
                        return
                for i, t in enumerate(reversed(word_types)):
                    if not issubclass(types[len(types) - 1 - i], t):
                        errors.append((((0,0), (0,0)),
                           f"{ansi(word, 93)} expected arguments {format_types(word_types)}, got {format_types(types[len(types) - len(word_types):])}"
                        ))
                        return
                for _ in word_types:
                    types.pop()
                for t in lexicon[word][1]:
                    types.append(t)
            case tuple(content):
                check(content[2], lexicon, content[1], errors, True, content[0])
                print(format_types(content[0]), '->', format_types(content[1]))
            case value:
                types.append(type(value))
    return


def run(tokens: list[utils.Token], lexicon: dict[str, CallableWord], stack: list[utils.Value] | None = None) -> None:
    if stack is None: stack = list()
    for token in tokens:
        match token:
            case Word(word):
                lexicon[word][2](stack)
            case value:
                stack.append(value)
                #types.append(type(value))

def word(lexicon: dict[str, CallableWord], want_stack: bool = False) -> Callable[
    [FunctionType], Callable[[list[utils.Value]], None]]:
    def decorator(function: FunctionType):
        returns = list()
        if 'return' in function.__annotations__ and function.__annotations__['return'] is not None:
            if isinstance(function.__annotations__['return'], tuple):
                for arg in function.__annotations__['return']: returns.append(arg)
            else: returns.append(function.__annotations__['return'])

        args = list()
        if not want_stack:
            for name, type_of in function.__annotations__.items():
                if name != 'return': args.append(type_of)

        def result(stack: list[utils.Value]):
            if want_stack: push = function(stack)
            else:
                func_args = list()
                for _ in args: func_args.append(stack.pop())
                push = function(*reversed(func_args))
            if push is not None:
                if isinstance(push, tuple):
                    for item in push: stack.append(item)
                else: stack.append(push)

        lexicon[function.__name__] = (args, returns, result)
        return result

    return decorator
