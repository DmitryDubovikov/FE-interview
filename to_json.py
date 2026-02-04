from typing import Any


def to_json(obj: Any) -> str:
    # None / bool
    if obj is None:
        return "null"
    if obj is True:
        return "true"
    if obj is False:
        return "false"

    # числа
    if isinstance(obj, (int, float)):
        return str(obj)

    # строки
    if isinstance(obj, str):
        escaped = obj.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    # dict
    if isinstance(obj, dict):
        items = []
        for k, v in obj.items():
            if not isinstance(k, str):
                raise TypeError("JSON keys must be strings")
            items.append(f'{to_json(k)}:{to_json(v)}')
        return "{" + ",".join(items) + "}"

    # списки / кортежи / множества
    if isinstance(obj, (list, tuple, set)):
        return "[" + ",".join(to_json(x) for x in obj) + "]"

    # fallback
    raise TypeError(f"Type not supported: {type(obj)}")

if __name__ == '__main__':
    res = to_json((1, 2, 3))
    print(res)


    