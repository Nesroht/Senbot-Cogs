import discord
from redbot.core import checks, Config, commands

import asyncio
import socket
from twitchbot import credentials

class Twitchbot(commands.Cog):
    """NSFW cog for Senbot"""

    def __init__(self, bot):
        self.bot = bot
        self.credentials = credentials
        self.channel = self.credentials.CHANNEL
        self.token = self.credentials.CLIENT_OAUTH
        self.nickname = self.credentials.CLIENT_USERNAME
        self.server = "irc.chat.twitch.tv"
        self.CHECK_DELAY = 1
        self.port = 6667

        self.sock = socket.socket()
        if credentials.CLIENT_ID is None:
            ctx.send("Please set twitchbot client ID with [p]twitchbot botset")
        else:
            self.helix = twitch.Helix(credentials.CLIENT_ID)
            self.messageListener()
            self.irc = socket.connect(self.server,self.port)
            self.connect()
            self.task = self.bot.loop.create_task(self.irc_check())


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
                    lambda message: self.messageHandler(message.channel, message.sender, message.text))
            return


    def messageHandler(self, channel, sender, text):
        test = sender
        if test is not self.credentials.CLIENT_USERNAME:
            print(channel +" "+ sender +" "+ text)
        else:
            if (text is "Ping!") and (test is self.credentials.CLIENT_USERNAME):
                print("Pong!")
        return

    async def connect(self):
        irc.send(f"PASS {self.token}\n".encode('utf-8'))
        irc.send(f"NICK {self.nickname}\n".encode('utf-8'))
        irc.send(f"JOIN {self.channel}\n".encode('utf-8'))

    async def irc_check(self):
        while True:
            try:
                await self.check_chat()
            except asyncio.CancelledError:
                pass
            await asyncio.sleep(self.CHECK_DELAY)

    async def check_chat(self):
        self.irc.setblocking(0)
        with contextlib.suppress(Exception):
            senderdata = self.irc.recv(2048)  # gets output from IRC server
            linecount = senderdata.count('\r\n')
            if senderdata.startsWith("PING"):
                self.irc.send("PONG\n".encode("utf-8"))
            elif linecount == 1:
                print(senderdata)
                print("Single message")
            elif senderdata.find('tmi.twitch.tv JOIN ' + channel) != -1:
                print(linecount - 1, 'People joined')
            elif senderdata.find('tmi.twitch.tv PART ' + channel) != -1:
                print(linecount - 1, 'People left')
            elif linecount > 1:
                print("Multiple messages")
                messagelist = []
                messagelist = senderdata.split('\r\n')
                print(len(messagelist))
                for i in range(0, len(messagelist)):
                    if (len(messagelist[i]) > 0):
                        print(messagelist[i])
                        print("message number: ")
                        print(i)
                    else:
                        print("This message is empty")
                        print(i)