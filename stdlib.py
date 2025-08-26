import utils
from core import word
from utils import format_list

builtins = {}

@word(builtins)
def add(a: int, b: int) -> int: return a + b

@word(builtins)
def sub(a: int, b: int) -> int: return a - b

@word(builtins)
def mul(a: int, b: int) -> int: return a * b

@word(builtins)
def mod(a: int, b: int) -> int: return a % b

@word(builtins)
def dup[T](a: T) -> (T, T): return a, a

@word(builtins)
def say(text: str) -> None: print(text)

@word(builtins, want_stack = True)
def peek(stack: list[utils.Value]) -> None: print(format_list(stack))

@word(builtins)
def pop(_: int) -> None: pass

py_quit = quit
@word(builtins)
def quit() -> None: py_quit()