import discord
import os
from discord.ext import commands, tasks
from random import choice
from config import config
from musicbot.audiocontroller import AudioController
from musicbot.settings import Settings
from musicbot import utils
from musicbot.utils import guild_to_audiocontroller, guild_to_settings

from musicbot.commands.general import General


initial_extensions = ['musicbot.commands.music',
                      'musicbot.commands.general', 'musicbot.plugins.button']
bot = commands.Bot(command_prefix=config.BOT_PREFIX, pm_help=True, case_insensitive=True)

status = ['Jamming out to music!', 'Eating!', 'Sleeping!', 'Translating!', 'Chilling']

if __name__ == '__main__':

    config.ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
    config.COOKIE_PATH = config.ABSOLUTE_PATH + config.COOKIE_PATH

    if config.BOT_TOKEN == "":
        print("Error: No bot token!")
        exit

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(e)


@bot.event
async def on_ready():
    change_status.start()
    print(config.STARTUP_MESSAGE)

    for guild in bot.guilds:
        await register(guild)
        print("Joined {}".format(guild.name))

    print(config.STARTUP_COMPLETE_MESSAGE)


@bot.event
async def on_guild_join(guild):
    print(guild.name)
    await register(guild)


async def register(guild):

    guild_to_settings[guild] = Settings(guild)
    guild_to_audiocontroller[guild] = AudioController(bot, guild)

    vc_channels = guild.voice_channels
    await guild.me.edit(nick=guild_to_settings[guild].get('default_nickname'))
    start_vc = guild_to_settings[guild].get('start_voice_channel')
    if start_vc != None:
        for vc in vc_channels:
            if vc.id == start_vc:
                await guild_to_audiocontroller[guild].register_voice_channel(vc_channels[vc_channels.index(vc)])
                await General.udisconnect(self=None, ctx=None, guild=guild)
                try:
                    await guild_to_audiocontroller[guild].register_voice_channel(vc_channels[vc_channels.index(vc)])
                except Exception as e:
                    print(e)
    else:
        await guild_to_audiocontroller[guild].register_voice_channel(guild.voice_channels[0])
        await General.udisconnect(self=None, ctx=None, guild=guild)
        try:
            await guild_to_audiocontroller[guild].register_voice_channel(guild.voice_channels[0])
        except Exception as e:
            print(e)

@tasks.loop(seconds=20)
async def change_status():
    await bot.change_presence(activity=discord.Game(choice(status)))


bot.run(config.BOT_TOKEN, bot=True, reconnect=True)
