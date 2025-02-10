def convert(content: int, characters: str) -> str:
    if content == 0: return ""
    return characters[content % len(characters)] + convert(content // len(characters), characters)