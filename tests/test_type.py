import pytest

from topgg import types

d: dict = {
    "invite": "https://top.gg/discord",
    "support": "https://discord.gg/dbl",
    "github": "https://github.com/top-gg",
    "longdesc": "A bot to grant API access to our Library Developers on the Top.gg site without them needing to submit a bot to pass verification just to be able to access the API.\n\nThis is not a real bot, so if you happen to find this page, do not try to invite it. It will not work.\n\nAccess to this bot's team can be requested by contacting a Community Manager in [our Discord server](https://top.gg/discord).",
    "shortdesc": "API access for Top.gg Library Developers",
    "prefix": "/",
    "lib": "",
    "clientid": "1026525568344264724",
    "avatar": "https://cdn.discordapp.com/avatars/1026525568344264724/cd70e62e41f691f1c05c8455d8c31e23.png",
    "id": "1026525568344264724",
    "username": "Top.gg Lib Dev API Access",
    "date": "2022-10-03T16:08:55.292Z",
    "server_count": 2,
    "shard_count": 0,
    "guilds": [],
    "shards": [],
    "monthlyPoints": 2,
    "points": 28,
    "certifiedBot": False,
    "owners": ["121919449996460033"],
    "tags": ["api", "library", "topgg"],
    "reviews": {"averageScore": 5, "count": 2},
}

query_dict = {"qwe": "1", "rty": "2", "uio": "3"}

vote_data_dict = {
    "type": "test",
    "query": "?" + "&".join(f"{k}={v}" for k, v in query_dict.items()),
    "user": "1",
}

bot_vote_dict = {
    "bot": "2",
    "user": "3",
    "type": "test",
    "query": "?" + "&".join(f"{k}={v}" for k, v in query_dict.items()),
    "isWeekend": False,
}

server_vote_dict = {
    "guild": "4",
    "user": "5",
    "type": "upvote",
    "query": "?" + "&".join(f"{k}={v}" for k, v in query_dict.items()),
}

bot_stats_dict = {"server_count": 2, "shards": [], "shard_count": 0}


@pytest.fixture
def bot_data() -> types.BotData:
    return types.BotData(**d)


@pytest.fixture
def widget_options() -> types.WidgetOptions:
    return types.WidgetOptions(
        id=int(d["id"]),
        project_type=types.WidgetProjectType.DISCORD_BOT,
        type=types.WidgetType.LARGE,
    )


@pytest.fixture
def vote_data() -> types.VoteDataDict:
    return types.VoteDataDict(**vote_data_dict)


@pytest.fixture
def bot_vote_data() -> types.BotVoteData:
    return types.BotVoteData(**bot_vote_dict)


@pytest.fixture
def server_vote_data() -> types.GuildVoteData:
    return types.GuildVoteData(**server_vote_dict)


@pytest.fixture
def bot_stats_data() -> types.BotStatsData:
    return types.BotStatsData(**bot_stats_dict)


def test_bot_data_fields(bot_data: types.BotData) -> None:
    bot_data.github = "I'm a GitHub link!"
    bot_data.support = "Support has arrived!"

    for attr in bot_data.__slots__:
        if "id" in attr.lower():
            value = getattr(bot_data, attr)

            assert isinstance(value, int) or value is None
        elif attr in ("owners", "guilds"):
            for item in getattr(bot_data, attr):
                assert isinstance(item, int)


def test_vote_data_fields(vote_data: types.VoteDataDict) -> None:
    assert isinstance(vote_data.query, dict)
    vote_data.type = "upvote"


def test_bot_vote_data_fields(bot_vote_data: types.BotVoteData) -> None:
    assert isinstance(bot_vote_data.query, dict)
    bot_vote_data.type = "upvote"

    assert isinstance(bot_vote_data.bot, int)


def test_server_vote_data_fields(server_vote_data: types.BotVoteData) -> None:
    assert isinstance(server_vote_data.query, dict)
    server_vote_data.type = "upvote"

    assert isinstance(server_vote_data.guild, int)


def test_bot_stats_data_attrs(bot_stats_data: types.BotStatsData) -> None:
    for count in ("server_count", "shard_count"):
        value = getattr(bot_stats_data, count)

        assert isinstance(value, int) or value is None

    assert isinstance(bot_stats_data.shards, list)

    if bot_stats_data.shards:
        for shard in bot_stats_data.shards:
            assert isinstance(shard, int)
