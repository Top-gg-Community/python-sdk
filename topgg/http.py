# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2021 Assanali Mukhanov

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Union

import aiohttp
from aiohttp import ClientResponse

from . import __version__, errors
from .ratelimiter import AsyncRateLimiter
from .types import DataDict

log = logging.getLogger(__name__)


async def _json_or_text(response: ClientResponse) -> Union[dict, str]:
    """

    Parameters
    ----------
    response: ClientResponse
        The received aiohttp response object.

    Returns
    -------
    body: Union[dict, str]
        Response body in either JSON or string.
    """
    text = await response.text()
    if response.headers["Content-Type"] == "application/json; charset=utf-8":
        return DataDict(**json.loads(text))
    return text


class HTTPClient:
    """Represents an HTTP client sending HTTP requests to the Top.gg API.

    .. _event loop: https://docs.python.org/3/library/asyncio-eventloops.html
    .. _aiohttp session: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

    Parameters
    ----------
    token:
        A Top.gg API Token.
    **session: `aiohttp session`_
        The `aiohttp session`_ used for requests to the API.
    **loop: `event loop`_
        An `event loop`_ used for asynchronous operations.
    """

    def __init__(self, token, **kwargs):
        self.BASE = "https://top.gg/api"
        self.token = token
        self.loop = kwargs.get("loop") or asyncio.get_event_loop()
        self.session = kwargs.get("session") or aiohttp.ClientSession(loop=self.loop)
        self.rate_limiter = AsyncRateLimiter(
            max_calls=59, period=60, callback=_ratelimit_handler
        )
        self.user_agent = (
            f"topggpy (https://github.com/top-gg/python-sdk {__version__}) Python/"
            f"{sys.version_info[0]}.{sys.version_info[1]} aiohttp/{aiohttp.__version__}"
        )

    async def request(self, method, url, **kwargs) -> Union[DataDict, str]:
        """Handles requests to the API."""
        url = f"{self.BASE}{url}"

        if not self.token:
            raise errors.UnauthorizedDetected("Top.gg API token not provided")

        headers = {
            "User-Agent": self.user_agent,
            "Content-Type": "application/json",
            "Authorization": self.token,
        }

        if "json" in kwargs:
            kwargs["data"] = to_json(kwargs.pop("json"))

        kwargs["headers"] = headers

        for _ in range(2):
            async with self.rate_limiter:
                async with self.session.request(method, url, **kwargs) as resp:
                    log.debug(
                        "%s %s with %s has returned %s",
                        method,
                        url,
                        kwargs.get("data"),
                        resp.status,
                    )

                    data = await _json_or_text(resp)

                    if 300 > resp.status >= 200:
                        return data

                    elif resp.status == 429:  # we are being ratelimited
                        fmt = "We are being ratelimited. Retrying in %.2f seconds (%.3f minutes)."

                        # sleep a bit
                        retry_after = float(resp.headers.get("Retry-After"))
                        mins = retry_after / 60
                        log.warning(fmt, retry_after, mins)

                        # check if it's a global ratelimit (True as only 1 ratelimit atm - /api/bots)
                        # is_global = True
                        # is_global = data.get('global', False)
                        # if is_global:
                        #     self._global_over.clear()

                        await asyncio.sleep(retry_after, loop=self.loop)
                        log.debug("Done sleeping for the ratelimit. Retrying...")

                        # release the global lock now that the
                        # global ratelimit has passed
                        # if is_global:
                        #     self._global_over.set()
                        log.debug("Global ratelimit is now over.")
                        continue

                    elif resp.status == 400:
                        raise errors.HTTPException(resp, data)
                    elif resp.status == 401:
                        raise errors.Unauthorized(resp, data)
                    elif resp.status == 403:
                        raise errors.Forbidden(resp, data)
                    elif resp.status == 404:
                        raise errors.NotFound(resp, data)
                    elif resp.status >= 500:
                        raise errors.ServerError(resp, data)

        # We've run out of retries, raise.
        raise errors.HTTPException(resp, data)

    async def close(self):
        await self.session.close()

    async def post_guild_count(self, guild_count, shard_count, shard_id):
        """Posts bot's guild count and shards info on Top.gg."""
        payload = {"server_count": guild_count}
        if shard_count:
            payload["shard_count"] = shard_count
        if shard_id:
            payload["shard_id"] = shard_id

        await self.request("POST", "/bots/stats", json=payload)

    async def get_weekend_status(self):
        """Gets the weekend status from Top.gg."""
        return await self.request("GET", "/weekend")

    async def get_guild_count(self, bot_id):
        """Gets the guild count of the given Bot ID."""
        return await self.request("GET", f"/bots/{bot_id}/stats")

    async def get_bot_info(self, bot_id):
        """Gets the information of a bot under given bot ID on Top.gg."""
        return await self.request("GET", f"/bots/{bot_id}")

    async def get_bot_votes(self, bot_id):
        """Gets your bot's last 1000 votes on Top.gg."""
        return await self.request("GET", f"/bots/{bot_id}/votes")

    async def get_bots(self, limit, offset, sort, search, fields):
        """Gets an object of bots on Top.gg."""
        if limit > 500:
            limit = 50
        fields = ", ".join(fields)
        search = " ".join([f"{field}: {value}" for field, value in search.items()])

        return await self.request(
            "GET",
            "/bots",
            params={
                "limit": limit,
                "offset": offset,
                "sort": sort,
                "search": search,
                "fields": fields,
            },
        )

    async def get_user_info(self, user_id):
        """Gets an object of the user on Top.gg."""
        return await self.request("GET", f"/users/{user_id}")

    async def get_user_vote(self, bot_id, user_id):
        """Gets info whether the user has voted for your bot."""
        return await self.request(
            "GET", f"/bots/{bot_id}/check", params={"userId": user_id}
        )


async def _ratelimit_handler(until):
    """Handles the displayed message when we are ratelimited."""
    duration = round(until - datetime.utcnow().timestamp())
    mins = duration / 60
    fmt = (
        "We have exhausted a ratelimit quota. Retrying in %.2f seconds (%.3f minutes)."
    )
    log.warning(fmt, duration, mins)


def to_json(obj):
    if json.__name__ == "ujson":
        return json.dumps(obj, ensure_ascii=True)
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=True)
