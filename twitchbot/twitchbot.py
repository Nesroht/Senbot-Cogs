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
        self.channels = {"nesroht"}
        self.messageListener()


    @commands.command()
    async def test(self, ctx, channel):
        await ctx.send("Testing connection to twitch")
        twitch.Chat(channel='#' + channel, nickname=self.credentials.CLIENT_USERNAME,
                    oauth=credentials.CLIENT_OAUTH).send("Ping!")

    async def messageListener(self):
        for channel in self.channels:
            twitch.Chat(channel='#'+channel, nickname=self.credentials.CLIENT_USERNAME, oauth=self.credentials.CLIENT_OAUTH).subscribe(
                await self.messageHandler(channel=message.channel, sender=message.sender, text=message.text, helix=message.helix))
        return


    async def messageHandler(self, *, channel, sender, text, helix):
        user = helix.user(message.sender).displayname
        if user is not self.credentials.CLIENT_USERNAME:
            print(channel, user, text)
        else:
            if (text is "Ping!") and (user is self.credentials.CLIENT_USERNAME):
                print("Pong!")