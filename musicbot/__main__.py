import sys
from traceback import print_exc

import discord

# import bridge here to override discord.Option with BridgeOption
from discord.ext import commands, bridge

from config import config
from musicbot import loader
from musicbot.bot import MusicBot
from musicbot.utils import check_dependencies, read_shutdown

del bridge

initial_extensions = [
    "musicbot.commands.music",
    "musicbot.commands.general",
]


intents = discord.Intents.default()
intents.voice_states = True
if config.BOT_PREFIX:
    intents.message_content = True
    prefix = config.BOT_PREFIX
else:
    prefix = " "  # messages can't start with space
if config.MENTION_AS_PREFIX:
    prefix = commands.when_mentioned_or(prefix)

if config.ENABLE_BUTTON_PLUGIN:
    intents.message_content = True
    initial_extensions.append("musicbot.plugins.button")

bot = MusicBot(
    command_prefix=prefix,
    case_insensitive=True,
    status=discord.Status.online,
    activity=discord.Game(name=config.STATUS_TEXT),
    intents=intents,
    allowed_mentions=discord.AllowedMentions.none(),
)


if __name__ == "__main__":
    print("Loading...")

    check_dependencies()
    config.warn_unknown_vars()
    config.save()

    bot.load_extensions(*initial_extensions)

    # start executor before reading from stdin to avoid deadlocks
    loader.init()

    if "--run" in sys.argv:
        shutdown_task = bot.loop.create_task(read_shutdown())

    try:
        bot.run(config.BOT_TOKEN, reconnect=True)
    except discord.LoginFailure:
        print_exc(file=sys.stderr)
        print("Set the correct token in config.json", file=sys.stderr)
        sys.exit(1)
