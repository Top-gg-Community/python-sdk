"""
The MIT License (MIT)

Copyright (c) 2021 Norizon & Top.gg
Copyright (c) 2024-2025 null8626 & Top.gg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import inspect
import typing as t

from .errors import TopGGException


T = t.TypeVar('T')
DataContainerT = t.TypeVar('DataContainerT', bound='DataContainerMixin')


def data(type_: t.Type[T]) -> T:
    """
    The injected data. This should be set as the parameter's default value.

    .. code-block:: python

        client = topgg.DBLClient(os.getenv('BOT_TOKEN')).set_data(bot)
        autoposter = client.autopost()


        @autoposter.stats()
        def get_stats(bot: MyBot = topgg.data(MyBot)) -> topgg.StatsWrapper:
            return topgg.StatsWrapper(bot.server_count)

    :param type_: The type of the injected data.
    :type type_: Any

    :returns: The injected data.
    :rtype: T
    """

    return t.cast(T, Data(type_))


class Data(t.Generic[T]):
    __slots__ = ('type',)

    def __init__(self, type_: t.Type[T]) -> None:
        self.type = type_


class DataContainerMixin:
    """
    A data container.

    This is useful for injecting some data so that they're available as arguments in your functions.
    """

    __slots__ = ('_data',)

    def __init__(self) -> None:
        self._data = {type(self): self}

    def set_data(
        self: DataContainerT, data_: t.Any, *, override: bool = False
    ) -> DataContainerT:
        """
        Sets the data to be available in your functions.

        :param data_: The data to be injected.
        :type data_: Any
        :param override: Whether to override another instance that already exists. Defaults to :py:obj:`False`.
        :type override: :py:class:`bool`

        :exception TopGGException: Override is :py:obj:`False` and another instance of the same type already exists.

        :returns: The object itself.
        :rtype: :class:`.DataContainerMixin`
        """

        type_ = type(data_)

        if not override and type_ in self._data:
            raise TopGGException(
                f'{type_} already exists. If you wish to override it, pass True into the override parameter.'
            )

        self._data[type_] = data_

        return self

    @t.overload
    def get_data(self, type_: t.Type[T]) -> t.Optional[T]: ...

    @t.overload
    def get_data(self, type_: t.Type[T], default: t.Any = None) -> t.Any: ...

    def get_data(self, type_: t.Any, default: t.Any = None) -> t.Any:
        """
        Gets the injected data.

        :param type_: The type of the injected data.
        :type type_: Any
        :param default: The default value in case the injected data does not exist. Defaults to :py:obj:`None`.
        :type default: Any

        :returns: The injected data.
        :rtype: Any
        """

        return self._data.get(type_, default)

    async def _invoke_callback(
        self, callback: t.Callable[..., T], *args: t.Any, **kwargs: t.Any
    ) -> T:
        parameters: t.Mapping[str, inspect.Parameter]

        try:
            parameters = inspect.signature(callback).parameters
        except (ValueError, TypeError):
            parameters = {}

        signatures: dict[str, Data] = {
            k: v.default
            for k, v in parameters.items()
            if v.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
            and isinstance(v.default, Data)
        }

        for k, v in signatures.items():
            signatures[k] = self._resolve_data(v.type)

        res = callback(*args, **{**signatures, **kwargs})

        if inspect.isawaitable(res):
            return await res

        return res

    def _resolve_data(self, type_: t.Type[T]) -> T:
        return self._data[type_]
