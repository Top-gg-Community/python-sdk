# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2018 Francis Taylor

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
import aiohttp

from . import __version__ as library_version
from .errors import *
from .http import HTTPClient

BASE = 'https://discordbots.org/api'


class Client:

    def __init__(self, *, loop=None, **options):
        self.loop = loop or asyncio.get_event_loop()
        self.http = HTTPClient(loop=self.loop)
        self._is_closed = False

    async def post_server_count(self, id: int, token: str, guild_count: int, shard_count: int = None, shard_no: int = None):
        """This function is a coroutine.

        Posts the server count to discordbots.org

        Parameters
        ==========

        id: int
            The id of the bot you want to post the server count of.
        token:
            The DBL Bot token. Visit https://discordbots.org/api to generate one.
        guild_count: int
            The number of guilds the bot (or current shard) is in.
        shard_count: int
            (Optional) The total number of shards.
        shard_no: int
            (Optional) The index of the current shard. DBL uses 0 indexed shards (the first shard is 0).

        Raises
        ======

        400
            Bad Request. You should not repeat this request without modification of your code.
        401
            Unauthorized. Check your DBL token.
        403
            Forbidden. You can't access this resource.
        404
            Page not found. Unlikely, but probably caused by maintenance. Try again later.
        429
            You are being ratelimited.
        500
            Internal Server Error. The server encountered an unexpected condition that prevented it from fulfilling the request."""

        await self.http.post_server_count(id, token, guild_count, shard_count, shard_no)

    async def get_server_count(self, id: int):
        """This function is a coroutine.

        Gets a server count from discordbots.org

        Parameters
        ==========

        id: int
            The id of the bot you want to lookup.

        Returns
        =======

        count: int
            The number of servers the bot is on.

        Raises
        ======

        400
            Bad Request. You should not repeat this request without modification of your code.
        401
            Unauthorized. Check your DBL token.
        403
            Forbidden. You can't access this resource.
        404
            Page not found. Unlikely, but probably caused by maintenance. Try again later.
        429
            You are being ratelimited.
        500
            Internal Server Error. The server encountered an unexpected condition that prevented it from fulfilling the request."""
        return await self.http.get_server_count(id)

    async def get_upvote_count(self, id: int):
        """This function is a coroutine.

        Gets the upvote count of a bot from discordbots.org

        Parameters
        ==========

        id: int
            The id of the bot you want to lookup.

        Returns
        =======

        votes: int
            The number of upvotes the bot has received.

        Raises
        ======

        400
            Bad Request. You should not repeat this request without modification of your code.
        401
            Unauthorized. Check your DBL token.
        403
            Forbidden. You can't access this resource.
        404
            Page not found. Unlikely, but probably caused by maintenance. Try again later.
        429
            You are being ratelimited.
        500
            Internal Server Error. The server encountered an unexpected condition that prevented it from fulfilling the request."""

        return await self.http.get_upvote_count(id)

    async def get_upvote_info(self, id: int, token: str, onlyids: bool = False):
        """This function is a coroutine.

        Gets information about who upvoted a bot from discordbots.org
        Available to the owner of the bot only.

        Parameters
        ==========

        id: int
            The id of the bot you want to lookup.
        token: str
            The DBL token. Visit https://discordbots.org/api to generate one.
        onlyids: bool
            If true, will return only the ids of who upvoted your bot.

        Returns
        =======

        votes: json
            A json object containing info about who upvoted a bot.

        Raises
        ======

        400
            Bad Request. You should not repeat this request without modification of your code.
        401
            Unauthorized. Check your DBL token.
        403
            Forbidden. You can't access this resource.
        404
            Page not found. Unlikely, but probably caused by maintenance. Try again later.
        429
            You are being ratelimited.
        500
            Internal Server Error. The server encountered an unexpected condition that prevented it from fulfilling the request."""

        return await self.http.get_upvote_info(id, token, onlyids)

    async def get_bot_info(self, id: int):
        """This function is a coroutine.

        Gets information about a bot from discordbots.org

        Parameters
        ==========

        id: int
            The id of the bot you want to lookup.

        Returns
        =======

        defAvatar: str
            The id of the default avatar of the bot.
        avatar: str
            The id of the bots avatar. Use `https://discordapp.com/assets/{:avatar}.png`
        invite: str
            The instant invite URL.
        github: str
            The URL of the Github repository.
        website: str
            The website of the bot.
        intdesc: str
            The raw contents of the bots int description.
        shortdesc: str
            The bots short description.
        prefix: str
            The prefix of the bot.
        lib: str
            The library wrapper the bot was written in.
        clientid: int
            The Client ID of the bot. Used in the instant invite URL.
        id: int
            The ID of the bot.
        username: str
            The name of the bot.
        discrim: int
            The discriminator of the bot.
        date: datetime
            The datetime object of when the bot was added to DBL.
        server_count: int
            The server count of the bot.
        shard_count: int
            The shard count of the bot.
        vanity: str
            The DBL vanity URL of the bot (partnered bots only).
        support: str
            The invite code for the bots support server.
        shards: json
            JSON object containing information about individual shards and their server count.
        points: int
            The number of upvotes the bot has.
        certifiedBot: bool
            Whether the bot is certified.
        owners: json
            JSON object containing a list of the bot owners.
        tags: json
            JSON object containing a list of tags.
        legacy: bool
            Is the bot using the old profile format? True if the bot hasn't been edited since 2017-12-31.

        Raises
        ======

        400
            Bad Request. You should not repeat this request without modification of your code.
        401
            Unauthorized. Check your DBL token.
        403
            Forbidden. You can't access this resource.
        404
            Page not found. Unlikely, but probably caused by maintenance. Try again later.
        429
            You are being ratelimited.
        500
            Internal Server Error. The server encountered an unexpected condition that prevented it from fulfilling the request."""

        return await self.http.get_bot_info(id)

    async def get_bots(self, limit: int = 50, offset: int = 0):
        """This function is a coroutine.

        Gets information about listed bots on discordbots.org

        Parameters
        ==========

        limit: int
            The number of results you wish to lookup. Leave blank for max (50).
        offset: int
            The page number to search. Leave blank for default (0).

        Returns
        =======

        bots
            Returns all of the bots in json format.

        Raises
        ======

        400
            Bad Request. You should not repeat this request without modification of your code.
        403
            Forbidden. You can't access this resource.
        404
            Page not found.
        429
            You are being ratelimited.
        500
            Internal Server Error. The server encountered an unexpected condition that prevented it from fulfilling the request."""

        return await self.http.get_bots(limit, offset)

    async def get_user(self, id: int):
        """This function is a coroutine.

        Gets information about a user on discordbots.org

        Parameters
        ==========

        id: int
            The id of the user you wish to lookup.

        Returns
        =======

        user_data
            Returns information about the user in json format.

        Raises
        ======

        400
            Bad Request. You should not repeat this request without modification of your code.
        403
            Forbidden. You can't access this resource.
        404
            Page not found.
        429
            You are being ratelimited.
        500
            Internal Server Error. The server encountered an unexpected condition that prevented it from fulfilling the request."""

        return await self.http.get_user(id)

    async def generate_widget_large(self, id: int, top: str = '2C2F33', mid: str = '23272A', user: str = 'FFFFFF', cert: str = 'FFFFFF', data: str = 'FFFFFF', label: str = '99AAB5', highlight: str = '2C2F33'):
        """This function is a coroutine.

        #` to the color codes (e.g. #FF00FF become FF00FF).
        Generates a custom large widget. Do not add `


        Parameters
        ==========

        id: int
            The id of the bot you wish to make a widget for.
        top: str
            The hex color code of the top bar.
        mid: str
            The hex color code of the main section.
        user: str
            The hex color code of the username text.
        cert: str
            The hex color code of the certified text (if applicable).
        data: str
            The hex color code of the statistics (numbers only e.g. 44) of the bot .
        label: str
            The hex color code of the description (text e.g. server count) of the statistics.
        highlight: str
            The hex color code of the data boxes.

        Returns
        =======

        URL with the widget.

        Raises
        ======

        400
            Bad Request. You should not repeat this request without modification of your code.
        403
            Forbidden. You can't access this resource.
        404
            Page not found.
        429
            You are being ratelimited.
        500
            Internal Server Error. The server encountered an unexpected condition that prevented it from fulfilling the request.
        """

        url = 'https://discordbots.org/api/widget/{0}.png?topcolor={1}&middlecolor={2}&usernamecolor={3}&certifiedcolor={4}&datacolor={5}&labelcolor={6}&highlightcolor={7}'.format(
            id, top, mid, user, cert, data, label, highlight)
        return url

    async def get_widget_large(self, id: int):
        """This function is a coroutine.

        Generates the default large widget.

        Parameters
        ==========

        id: int
            The id of the bot you wish to make a widget for.

        Returns
        =======

        URL with the widget.

        Raises
        ======

        400
            Bad Request. You should not repeat this request without modification of your code.
        403
            Forbidden. You can't access this resource.
        404
            Page not found.
        429
            You are being ratelimited.
        500
            Internal Server Error. The server encountered an unexpected condition that prevented it from fulfilling the request.
        """
        url = 'https://discordbots.org/api/widget/{0}.png'.format(id)
        return url

    async def generate_widget_small(self, id: int, avabg: str = '2C2F33', lcol: str = '23272A', rcol: str = '2C2F33', ltxt: str = 'FFFFFF', rtxt: str = 'FFFFFF'):
        """This function is a coroutine.

        #` to the color codes (e.g. #FF00FF become FF00FF).
        Generates a custom large widget. Do not add `

        Parameters
        ==========

        id: int
            The id of the bot you wish to make a widget for.
        avabg: str
            The hex color code of the background of the avatar (if the avatar has transparency).
        lcol: str
            The hex color code of the left background color.
        rcol: str
            The hex color code of the right background color.
        ltxt: str
            The hex color code of the left text.
        rtxt: str
            The hex color code of the right text.

        Returns
        =======

        URL with the widget.

        Raises
        ======

        400
            Bad Request. You should not repeat this request without modification of your code.
        403
            Forbidden. You can't access this resource.
        404
            Page not found.
        429
            You are being ratelimited.
        500
            Internal Server Error. The server encountered an unexpected condition that prevented it from fulfilling the request.
        """

        url = 'https://discordbots.org/api/widget/lib/{0}.png?avatarbg={1}&lefttextcolor={2}&righttextcolor={3}&leftcolor={4}&rightcolor={5}'.format(
            id, avabg, ltxt, rtxt, lcol, rcol)

        return url

    async def get_widget_small(self, id: int):
        """This function is a coroutine.

        Generates the default small widget.

        Parameters
        ==========

        id: int
            The id of the bot you wish to make a widget for.

        Returns
        =======

        URL with the widget.

        Raises
        ======

        400
            Bad Request. You should not repeat this request without modification of your code.
        403
            Forbidden. You can't access this resource.
        404
            Page not found.
        429
            You are being ratelimited.
        500
            Internal Server Error. The server encountered an unexpected condition that prevented it from fulfilling the request.
        """

        url = 'https://discordbots.org/api/widget/lib/{0}.png'.format(id)
        return url

    async def close(self):
        """This function is a coroutine.
        Closes all connections."""
        if self._is_closed:
            return
        else:
            await self.http.close()
            self._is_closed = True

    @property
    def is_closed(self):
        """bool: Indicates if the websocket connection is closed."""
        return self._closed.is_set()
