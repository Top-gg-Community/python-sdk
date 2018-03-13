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
#import string
#import random
import logging

from . import __version__ as library_version
from .http import HTTPClient
#from .errors import InvalidArgument

log = logging.getLogger(__name__)


class Client:
    """Represents a client connection that connects to discordbots.org.
    This class is used to interact with the DBL API.

    .. _event loop: https://docs.python.org/3/library/asyncio-eventloops.html
    .. _aiohttp session: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

    Parameters
    ==========

    token :
        An API Token

    bot :
        An instance of a discord.py Bot or Client object
    **loop : Optional[event loop].
        The `event loop`_ to use for asynchronous operations.
        Defaults to ``bot.loop``.
    **session : Optional
        The aiohttp session to use for requests to the API.
    """

    def __init__(self, bot, token, **kwargs):
        self.bot = bot
        self.bot_id = None
        self.loop = kwargs.get('loop') or bot.loop
        self.http = HTTPClient(token, loop=self.loop, session=kwargs.get('session'))
        self._is_closed = False
        self.loop.create_task(self.__ainit__())
        # print(self.loop.run_until_complete(bot.application_info()).id)

    async def __ainit__(self):
        await self.bot.wait_until_ready()
        self.bot_id = self.bot.user.id

    def guild_count(self):
        """Gets the guild count from the bot object"""
        try:
            return len(self.bot.guilds)
        except AttributeError:
            return len(self.bot.servers)

    async def post_server_count(
            self,
            shard_count: int = None,
            shard_no: int = None
    ):
        """This function is a coroutine.

        Posts the server count to discordbots.org

        .. _0 based indexing : https://en.wikipedia.org/wiki/Zero-based_numbering

        Parameters
        ==========

        shard_count: int[Optional]
            The total number of shards.
        shard_no: int[Optional]
            The index of the current shard. DBL uses `0 based indexing`_ for shards.
        """
        await self.http.post_server_count(self.bot_id, self.guild_count(), shard_count, shard_no)

    async def get_server_count(self, bot_id: int=None):
        """This function is a coroutine.

        Gets a server count from discordbots.org

        Parameters
        ==========

        bot_id: int[Optional]
            The bot_id of the bot you want to lookup.
            Defaults to the Bot provided in Client init

        Returns
        =======

        stats: dict
            The server count and shards of a bot.
            The date object is returned in a datetime.datetime object

        """
        if bot_id is None:
            bot_id = self.bot_id
        return await self.http.get_server_count(bot_id)

    async def get_upvote_info(self, **kwargs):
        """This function is a coroutine.

        Gets information about who upvoted a bot from discordbots.org

        .. note::

            This API endpoint is available to the owner of the bot only.

        Parameters
        ==========

        **onlyids: bool[Optional]
            Whether to return an array of simple user objects or an array of user ids.
            Defaults to False
        **days: int[Optional]
            Limits the votes to ones done within the amount of days you specify.
            Defaults to 31

        Returns
        =======

        votes: dict
            Info about who upvoted your bot.

        """
        bot_id = kwargs.get('bot_id', self.bot_id)
        onlyids = kwargs.get('onlyids', False)
        days = kwargs.get('days', 31)

        return await self.http.get_upvote_info(bot_id, onlyids, days)

    async def get_bot_info(self, bot_id: int = None):
        """This function is a coroutine.

        Gets information about a bot from discordbots.org

        Parameters
        ==========

        bot_id: int[Optional]
            The bot_id of the bot you want to lookup.

        Returns
        =======

        bot info: dict
            Information on the bot you looked up.
            https://discordbots.org/api/docs#bots
        """
        if bot_id is None:
            bot_id = self.bot_id
        return await self.http.get_bot_info(bot_id)

    async def get_bots(self, limit: int = 50, offset: int = 0):
        """This function is a coroutine.

        Gets information about listed bots on discordbots.org

        Parameters
        ==========

        limit: int[Optional]
            The number of results you wish to lookup. Defaults to 50.
        offset: int[Optional]
            The page number to search. Defaults to 0.

        Returns
        =======

        bots: dict
            Returns info on the bots on DBL.
            https://discordbots.org/api/docs#bots
        """
        return await self.http.get_bots(limit, offset)
    #
    # async def search_bots(self, limit: int = 50, offset: int = 0, **kwargs):
    #     """This function is a coroutine.
    #
    #     Searches bots on discordbots.org via the API
    #
    #     Parameters
    #     ==========
    #
    #     limit: int
    #         (Optional) The number of results you wish to lookup. Defaults to 50.
    #     offset: int
    #         (Optional) The page number to search. Defaults to 0.
    #     tag: str
    #         Keyword argument that specifies the tag to search.
    #     library: str
    #         Keyword argument that specifies the library to search.
    #
    #
    #     Returns
    #     =======
    #
    #     bots: json
    #         Returns bots matching your search results.
    #     """
    #     query = ''
    #     if 'tag' in kwargs:
    #         query = f'tag:{tag}'
    #     if 'library' in kwargs:
    #         query = f'library:{library}'

    #   return await self.http.search_bots(limit, offset, query=query)

    async def get_user_info(self, user_id: int):
        """This function is a coroutine.

        Gets information about a user on discordbots.org

        Parameters
        ==========

        user_id: int
            The user_id of the user you wish to lookup.

        Returns
        =======

        user_data: dict
            Info about the user.
            https://discordbots.org/api/docs#users
        """
        return await self.http.get_user_info(user_id)

    async def generate_widget_large(
            self,
            bot_id: int = None,
            top: str = '2C2F33',
            mid: str = '23272A',
            user: str = 'FFFFFF',
            cert: str = 'FFFFFF',
            data: str = 'FFFFFF',
            label: str = '99AAB5',
            highlight: str = '2C2F33'
    ):
        """This function is a coroutine.

        Generates a custom large widget. Do not add `#` to the color codes (e.g. #FF00FF become FF00FF).

        Parameters
        ==========

        bot_id: int
            The bot_id of the bot you wish to make a widget for.
        top: str
            The hex color code of the top bar.
        mid: str
            The hex color code of the main section.
        user: str
            The hex color code of the username text.
        cert: str
            The hex color code of the certified text (if applicable).
        data: str
            The hex color code of the statistics (numbers only e.g. 44) of the bot.
        label: str
            The hex color code of the description (text e.g. server count) of the statistics.
        highlight: str
            The hex color code of the data boxes.

        Returns
        =======

        URL of the widget: str
        """
        if bot_id is None:
            bot_id = self.bot_id
        url = 'https://discordbots.org/api/widget/{0}.png?topcolor={1}&middlecolor={2}&usernamecolor={3}&certifiedcolor={4}&datacolor={5}&labelcolor={6}&highlightcolor={7}'.format(
            bot_id, top, mid, user, cert, data, label, highlight)
        return url

    async def get_widget_large(self, bot_id: int = None):
        """This function is a coroutine.

        Generates the default large widget.

        Parameters
        ==========

        bot_id: int
            The bot_id of the bot you wish to make a widget for.

        Returns
        =======

        URL of the widget: str
        """
        if bot_id is None:
            bot_id = self.bot_id
        url = 'https://discordbots.org/api/widget/{0}.png'.format(bot_id)
        return url

    async def generate_widget_small(
            self,
            bot_id: int = None,
            avabg: str = '2C2F33',
            lcol: str = '23272A',
            rcol: str = '2C2F33',
            ltxt: str = 'FFFFFF',
            rtxt: str = 'FFFFFF'
    ):
        """This function is a coroutine.

        Generates a custom large widget. Do not add `#` to the color codes (e.g. #FF00FF become FF00FF).

        Parameters
        ==========

        bot_id: int
            The bot_id of the bot you wish to make a widget for.
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

        URL of the widget: str
        """
        if bot_id is None:
            bot_id = self.bot_id
        url = 'https://discordbots.org/api/widget/lib/{0}.png?avatarbg={1}&lefttextcolor={2}&righttextcolor={3}&leftcolor={4}&rightcolor={5}'.format(
            bot_id, avabg, ltxt, rtxt, lcol, rcol)

        return url

    async def get_widget_small(self, bot_id: int = None):
        """This function is a coroutine.

        Generates the default small widget.

        Parameters
        ==========

        bot_id: int
            The bot_id of the bot you wish to make a widget for.

        Returns
        =======

        URL of the widget: str
        """
        if bot_id is None:
            bot_id = self.bot_id
        url = 'https://discordbots.org/api/widget/lib/{0}.png'.format(bot_id)
        return url

    # async def start_vote_post(self, url: str = None, auth: str = None):
    #     """This function is a coroutine.
    #
    #     Sets up webhooks for posting a message to a Discord channel whenever someone votes on your bot.
    #
    #     .. note::
    #
    #         This function will automatically start a webserver to listen to incoming requests. You should point the webhooks to the IP or domain of your host.
    #
    #     Parameters
    #     ==========
    #
    #     auth: str[Optional]
    #         The authorization token (password) that will be used to verify requests coming back from DBL. Generate a random token with ``auth_generator()``
    #
    #     Returns
    #     =======
    #
    #     bot_id: int
    #         ID of the bot that received a vote.
    #     user_id: int        s.wfile.write('Hello!')
    #         ID of the user who voted.
    #     type: str
    #         The type of vote. 'upvote' or 'none' (unvote)
    #     query?: str
    #         Query string params found on the `/bot/:ID/vote` page.
    #     """
    #     if auth is None:
    #         log.warn(
    #             'Webhook validation token is Null. Please set one, or generate one using `auth_generator()`.')
    #
    #     await self.http.initialize_webhooks(url, auth)

    # async def auth_generator(self, size=32, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    #     """This function is a coroutine
    #
    #     Generates a random auth token for webhook validation."""
    #     return ''.join(random.SystemRandom().choice(chars) for _ in range(size))

    async def close(self):
        """This function is a coroutine.
        Closes all connections."""
        if self._is_closed:
            return
        else:
            await self.http.close()
            self._is_closed = True
