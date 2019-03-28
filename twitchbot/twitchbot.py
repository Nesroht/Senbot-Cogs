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
        self.channels = self.credentials.CHANNELS
        if credentials.CLIENT_ID is None:
            ctx.send("Please set twitchbot client ID with [p]twitchbot botset")
        else:
            self.helix = twitch.Helix(credentials.CLIENT_ID)
            self.messageListener()


    @commands.command()
    async def test(self, ctx, channel):
        if credentials.CLIENT_ID is None:
            await ctx.send("Please set twitchbot client ID with [p]twitchbot botset")
        else:
            await ctx.send("Testing connection to twitch")
            twitch.Chat(channel='#' + channel, nickname=self.credentials.CLIENT_USERNAME,
                        oauth=credentials.CLIENT_OAUTH).send("Ping!")

    @commands.group(name="twitchbot")
    async def _twitchbot(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help()
            return

    @_twitchbot.command()
    async def botset(self, ctx, *, client_id, client_username, client_oauth):
        self.credentials.CLIENT_USERNAME = client_username
        self.credentials.CLIENT_OAUTH = client_oauth
        self.credentials.CLIENT_ID = client_id
        await self.messageListener()

    def messageListener(self):
        if credentials.CLIENT_ID is None:
            return
        else:
            for channel in self.channels:
                twitch.Chat(channel='#'+channel, nickname=self.credentials.CLIENT_USERNAME, oauth=self.credentials.CLIENT_OAUTH).subscribe(
                    self.messageHandler(message.channel, message.sender, message.text))
            return


    def messageHandler(self, channel, sender, text):
        test = sender
        if test.upper() is not self.credentials.CLIENT_USERNAME.upper():
            print(channel +" "+ sender +" "+ text)
        else:
            if (text is "Ping!") and (test.upper() is self.credentials.CLIENT_USERNAME.upper()):
                print("Pong!")
        return