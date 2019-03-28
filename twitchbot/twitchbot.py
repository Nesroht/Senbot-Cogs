import discord
from redbot.core import checks, Config, commands

import asyncio
import twitch
from twitchbot import credentials

class Twitchbot(commands.Cog):
    """NSFW cog for Senbot"""

    def __init__(self, bot):
        self.bot = bot
        self.credentials = credentials
        self.helix = twitch.Helix(credentials.CLIENT_ID)


    @commands.command()
    async def test(self, ctx, channel):
        await ctx.send("Testing connection to twitch")
        try:
            self.messageHandler(channel)
            twitch.Chat(channel='#' + channel, nickname=self.credentials.CLIENT_USERNAME,
                        oauth=credentials.CLIENT_OAUTH).send("Testing connection to twitch")
        except Exception as e:
            print(e)

    async def messageHandler(self, channel):
        twitch.Chat(channel='#sodapoppin', nickname='zarlach', oauth='oauth:xxxxxx').subscribe(
            lambda message: print(message.channel, message.user().display_name, message.text))