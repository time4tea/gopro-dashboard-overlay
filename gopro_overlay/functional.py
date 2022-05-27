import functools
from typing import TypeVar, List

T = TypeVar("T")


def flatten(list_of_lists: List[List[T]]) -> List[T]:
    result = []

    def flatten_part(part):
        for item in part:
            if type(item) == list:
                flatten_part(item)
            else:
                result.append(item)

    flatten_part(list_of_lists)
    return result


def compose(*functions):
    return functools.reduce(lambda f, g: lambda x: f(g(x)), reversed(functions))
