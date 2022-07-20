from typing import Any, Callable


def optional_c(converter: Callable) -> Callable[..., Any]:
    """
    Handles conversion for possibly optional/missing values.

    Attributes
    ----------
    converter : `typing.Callable`
        The callable method to convert to.

        This could be a method or a class
        that is alone or `attrs`-based.

    Returns
    -------
    `typing.Callable[..., typing.Any]`
        Any possible value. If the value of
        the field is found to be `None` or
        `MISSING`, it will skip any given
        conversions. Otherwise, it will returned
        the converted value from `converter`.
    """

    def optional_converter(val):
        if val is None:
            return val
        return converter(val)

    return optional_converter


def list_c(func: Any) -> list[Any]:
    """
    Handles conversion for values nested inside of a list.

    ---

    This converter can be layered inside of `optional_c`,
    allowing for granular control over optional lists of
    values.

    ---

    Attributes
    ----------
    func : `typing.Any`
        The function or value to convert the list of.
        The function is needed as it's the presumed type
        of the converter when handled.

    Returns
    -------
    `list[typing.Any]`
        A list of values converted into what `func`
        has been provided with.
    """

    def inner(val):
        return [func(_) for _ in val]

    return inner
