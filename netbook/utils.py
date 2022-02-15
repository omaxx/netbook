from typing import Any, Union, Iterator
from collections.abc import Mapping, MutableMapping

SEPARATOR = "."
CLS = dict


def s_get(
        obj: Mapping[str, Any],
        key: Union[str, tuple[str, ...], list[str]],
        default=None
) -> Any:
    if obj is None:
        return None
    if not hasattr(obj, "__getitem__"):
        raise TypeError(f"'{type(obj)}' object is not subscriptable (key={key})")
    if isinstance(key, str) and SEPARATOR in key:
        key = key.split(SEPARATOR)
    if isinstance(key, (tuple, list)) and len(key) == 1:
        key = key[0]

    if isinstance(key, str):
        if key == "*":
            return obj
        try:
            return obj[key]
        except (KeyError, ):
            return default
    elif isinstance(key, (tuple, list)):
        if key[0] == "*":
            return {
                k: s_get(obj[k], key[1:]) for k in obj.keys() if s_get(obj[k], key[1:])
            }
        try:
            return s_get(obj[key[0]], key[1:])
        except (KeyError, ):
            return default


def s_set(
        obj: MutableMapping[str, Any],
        key: Union[str, tuple[str, ...], list[str]],
        value: Any
) -> None:
    if not isinstance(obj, MutableMapping):
        raise TypeError(f"obj should be MutableMapping, obj type is {type(obj)}")
    if isinstance(key, str) and SEPARATOR in key:
        key = key.split(SEPARATOR)
    if isinstance(key, (tuple, list)) and len(key) == 1:
        key = key[0]
    if not isinstance(key, (tuple, list)):
        # if isinstance(key, str) and key.isnumeric():
        #     key = int(key)
        #
        if key not in obj:
            obj[key] = value
        elif not isinstance(value, MutableMapping):
            obj[key] = value
        else:
            s_update(obj, value)
    else:
        # if isinstance(key[0], str) and key[0].isnumeric():
        #     key[0] = int(key[0])
        #
        if key[0] not in obj:
            obj[key[0]] = CLS()
        s_set(obj[key[0]], key[1:], value)


def s_items(
        obj: Mapping[str, Any]
) -> Iterator[tuple[Union[str, tuple[str, ...]], Any]]:
    for key, value in obj.items():
        if not isinstance(value, Mapping) or value == {}:
            yield key, value
        else:
            for k, v in s_items(value):
                if isinstance(k, (tuple, list)):
                    yield ((key, *k), v)
                else:
                    yield ((key, k), v)


def s_update(
        obj: MutableMapping[str, Any],
        updater: Mapping[str, Any]
) -> MutableMapping:
    for key, value in s_items(updater):
        s_set(obj, key, value=value)
    return obj


def s_update_nonexist(
        obj: MutableMapping[str, Any],
        updater: Mapping[str, Any]
) -> MutableMapping:
    for key, value in s_items(updater):
        if s_get(obj, key) is None:
            s_set(obj, key, value=value)
    return obj
