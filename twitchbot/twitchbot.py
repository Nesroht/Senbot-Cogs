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
    async def test(self, ctx, *, channel, *, message):
        await ctx.send("Testing connection to twitch")
        twitch.Chat(channel='#'+channel, nickname=self.credentials.CLIENT_USERNAME, oauth=credentials.CLIENT_OAUTH).subscribe(
            print(message))