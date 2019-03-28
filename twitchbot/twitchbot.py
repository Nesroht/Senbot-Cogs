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
            await self.messageHandler(channel)
            twitch.Chat(channel='#' + channel, nickname=self.credentials.CLIENT_USERNAME,
                        oauth=credentials.CLIENT_OAUTH).send("Ping!")
        except Exception as e:
            await ctx.send(e)

    async def messageListener(self):
        for channel in self.channels:
            twitch.Chat(channel='#'+channel, nickname=self.credentials.CLIENT_USERNAME, oauth=self.credentials.CLIENT_OAUTH).subscribe(
                lambda message: self.messageHandler(message))


    async def messageHandler(self, message):
        user = message.helix.user(message.sender).display_name
        if message.helix.user(message.sender).displayname is not self.credentials.CLIENT_USERNAME:
            print(message.channel, user, message.text)
        else:
            if (message.text is "Ping!") and (user is self.credentials.CLIENT_USERNAME):
                print("Pong!")