# The MIT License (MIT)

# Copyright (c) 2021 Norizon

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import inspect
import typing as t

from topgg.errors import TopGGException

T = t.TypeVar("T")
DataContainerT = t.TypeVar("DataContainerT", bound="DataContainerMixin")


def data(type_: t.Type[T]) -> T:
    return t.cast(T, Data(type_))


class Data(t.Generic[T]):
    __slots__ = ("type",)

    def __init__(self, type_: t.Type[T]) -> None:
        self.type: t.Type[T] = type_


class DataContainerMixin:
    __slots__ = ("_data",)

    def __init__(self) -> None:
        self._data: t.Dict[t.Type, t.Any] = {type(self): self}

    def set_data(
        self: DataContainerT, data_: t.Any, *, override: bool = False
    ) -> DataContainerT:
        type_ = type(data_)
        if not override and type_ in self._data:
            raise TopGGException(
                f"{type_} already exists. If you wish to override it, pass True into the override parameter."
            )

        self._data[type_] = data_
        return self

    def get_data(self, type_: t.Type[T], default: t.Any = None) -> T:
        return self._data.get(type_, default)

    async def _invoke_callback(
        self, callback: t.Callable[..., T], *args: t.Any, **kwargs: t.Any
    ) -> T:
        parameters: t.Mapping[str, inspect.Parameter]
        try:
            parameters = inspect.signature(callback).parameters
        except (ValueError, TypeError):
            parameters = {}

        signatures: t.Dict[str, Data] = {
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
