import os

def create_path(path: list[str] | tuple[str]) -> None | str:
    if len(path) <= 0:
        return None
    elif len(path) == 1:
        return path[0]
    else:
        return os.path.join(path[0], *path[1:])

def check_dir(path: str | list[str] | tuple[str]):
    if type(path) == str: split = os.path.split(path)
    elif type(path) in [list, tuple]:
        split = path
        path = create_path(path)
    else: return

    if not (os.path.exists(path) and os.path.isdir(path)):
        if len(split) > 1:
            check_path = split[:-1]
            check_dir(check_path)

        os.mkdir(path)