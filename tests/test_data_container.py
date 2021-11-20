import mock
import pytest

from topgg.data import DataContainerMixin, data


@pytest.fixture
def data_container() -> DataContainerMixin:
    dc = DataContainerMixin()
    dc.set_data("TEXT")
    dc.set_data(200)
    dc.set_data({"a": "b"})
    return dc


async def _async_callback(
    text: str = data(str), number: int = data(int), mapping: dict = data(dict)
):
    ...


def _sync_callback(
    text: str = data(str), number: int = data(int), mapping: dict = data(dict)
):
    ...


@pytest.mark.asyncio
async def test_data_container_invoke_async_callback(data_container: DataContainerMixin):
    await data_container._invoke_callback(_async_callback)


@pytest.mark.asyncio
async def test_data_container_invoke_sync_callback(data_container: DataContainerMixin):
    await data_container._invoke_callback(_sync_callback)
