from __future__ import annotations
from dataclasses import dataclass

def ansi(text: str, *codes: int) -> str: return f'\x1b[{';'.join(map(str, codes))}m{text}\x1b[0m'
def format_type(t: type) -> str: return ansi(t.__name__, 34)
def format_types(types: list[type]) -> str: return f'({', '.join(map(format_type, types))})'

@dataclass
class Word: word: str

@dataclass
class Keyword: word: str

@dataclass
class Brackets: tokens: list[Token]

type Value = int | float | str | bool | tuple[list[type], list[type], list[Token]]
type Token = Value | Word | Keyword | Brackets

def format_value(value: Value) -> str:
    match value:
        case bool(v):
            return ansi(str(v).lower(), 35)
        case int(v):
            return ansi(str(v), 36)
        case float(v):
            return ansi(str(v), 36)
        case str(v):
            return ansi(f"'{v}'", 31)
        case list(v):
            return f'{'{'}{format_list(v)}{'}'}'
    return '' #To appease the typechecker gods.

def format_token(token: Token) -> str:
    match token:
        case Word(word):
            return ansi(word, 93)
        case Keyword(word):
            return ansi(word, 90)
        case Brackets(expression):
            return f'({format_list(expression)})'
        case d:
            return format_value(d)

def format_list(l: list[Token]) -> str: return ' '.join(map(format_token, l))