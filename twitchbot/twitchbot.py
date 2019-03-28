import discord
from redbot.core import checks, Config, commands

import asyncio
import socket

import select

from twitchbot import credentials
from twitchbot import users

class Twitchbot(commands.Cog):
    """NSFW cog for Senbot"""

    def __init__(self, bot):
        self.bot = bot
        self.credentials = credentials
        self.channel = self.credentials.CHANNEL
        self.token = self.credentials.CLIENT_OAUTH
        self.nickname = self.credentials.CLIENT_USERNAME
        self.server = "irc.chat.twitch.tv"
        self.databuffer = []

        self.userlist = self.users.USERS

        self.CHECK_DELAY = 1
        self.port = 6667
        self.sock = {}
        self.task = {}

        if credentials.CLIENT_ID is None:
            ctx.send("Please set twitchbot client ID with [p]twitchbot botset")
        else:
            for channel in self.credentials.CHANNEL:
                self.sock[channel] = socket.socket()
                self.task[channel] = self.bot.loop.create_task(self.irc_check(channel))

    def __unload(self):
        for channel in self.credentials.CHANNEL:
            self.task[channel].cancel()
            self.sock[channel].close()


    @commands.command()
    async def test(self, ctx, channel,*, message):
        print(channel + " " + message)
        allowed = False
        if credentials.CLIENT_ID is None:
            await ctx.send("Please set twitchbot client ID with [p]twitchbot botset")
        else:
            for testchannel in self.credentials.CHANNEL:
                if channel == testchannel:
                    await ctx.send("Testing connection to twitch")
                    self.sock[channel].send(f"PRIVMSG #{channel} :{message}\r\n".encode("utf-8"))
                    allowed = True
            if allowed is False:
                await ctx.send(f"Can\'t test connection to {channel} because not connected to it!")

    @commands.command()
    async def link(self, ctx):
        await ctx.send(ctx.author)
        #self.userlist[users].append({"twitchuser": twitchuser, "discordid": ctx.author})

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


    """async def connect(self):
        self.sock[channel].send(f"PASS {self.token}\r\n".encode('utf-8'))
        self.sock[channel].send(f"NICK {self.nickname}\r\n".encode('utf-8'))
        resp = self.sock[channel].recv(2048).decode("utf-8")
        print(resp)
        self.sock[channel].send(f"JOIN #{self.channel}\r\n".encode('utf-8'))
        resp = self.sock[channel].recv(2048).decode("utf-8")
        resp = self.sock[channel].recv(2048).decode("utf-8")
        print(resp)
        self.sock[channel].send(f"PRIVMSG #{self.channel}:Successfully connected to chat! <3\r\n".encode("utf-8"))"""

    async def check_bal(self, origin, sender, channel):
        balance = 123 #Change this later
        if "twitch" in origin:
            self.sock[channel].send(f"PRIVMSG #{channel} :{sender}\'s balance is {balance}\r\n".encode("utf-8"))

    async def irc_check(self, channel):
        self.sock[channel].connect((self.server, self.port))
        self.sock[channel].send(f"PASS {self.token}\r\n".encode('utf-8'))
        self.sock[channel].send(f"NICK {self.nickname}\r\n".encode('utf-8'))
        resp = self.sock[channel].recv(2048).decode("utf-8")
        self.sock[channel].send(f"JOIN #{channel}\r\n".encode('utf-8'))
        resp = self.sock[channel].recv(2048).decode("utf-8")#
        self.sock[channel].send(f"PRIVMSG #{channel} :Successfully connected to chat! <3\r\n".encode("utf-8"))
        while True:
            try:
                ready = select.select([self.sock[channel]],[],[],1)
                if ready[0]:
                    senderdata = self.sock[channel].recv(2048).decode("utf-8")  # gets output from IRC server
                    #print(senderdata)
                    if "PING :tmi.twitch.tv" in senderdata:
                        self.sock[channel].send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                    elif "!bal" in senderdata:
                        #print("Baltest")
                        sender,dump = senderdata.split("!",1)
                        finish = sender[1:].capitalize()
                        await self.check_bal("twitch", finish, channel)
                    elif "!test" in senderdata:
                        #print("Success")
                        self.sock[channel].send(f"PRIVMSG #{channel} :Test successful!\r\n".encode("utf-8"))

                    await asyncio.sleep(self.CHECK_DELAY)
                    pass
                else:
                    await asyncio.sleep(self.CHECK_DELAY*2)
            except asyncio.CancelledError:
                pass
            await asyncio.sleep(self.CHECK_DELAY*2)
