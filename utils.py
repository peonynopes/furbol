def ansi(text: str, *codes: int) -> str: return f'\x1b[{';'.join(map(str, codes))}m{text}\x1b[0m'
def format_type(t: type) -> str: return ansi(t.__name__, 34)
def format_types(types: list[type]) -> str: return f'({', '.join(map(format_type, types))})'