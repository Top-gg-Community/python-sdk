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
import sys

import discord

import topgg


# these functions can be async too!
def on_autopost_success(
    # uncomment this if you want to get access to client
    # client: discord.Client = topgg.data(discord.Client)
):
    # will be called whenever it successfully posting
    print("Successfully posted!")

    # do whatever with client
    # you can dispatch your own event for more callbacks
    # client.dispatch("autopost_success")


def on_autopost_error(
    exception: Exception,
    # uncomment this if you want to get access to client
    # client: discord.Client = topgg.data(discord.Client),
):
    # will be called whenever it failed posting
    print("Failed to post", exception, file=sys.stderr)

    # do whatever with client
    # you can dispatch your own event for more callbacks
    # client.dispatch("autopost_error", exception)


def stats(client: discord.Client = topgg.data(discord.Client)):
    return topgg.StatsWrapper(guild_count=len(client.guilds))
