import discord
from redbot.core import checks, Config, commands

import asyncio
import bottom
from twitchbot import credentials

class Twitchbot(commands.Cog):
    """NSFW cog for Senbot"""

    twitchirc = bottom.Client(host=self.host, port=self.port, ssl=self.ssl)

    def __init__(self, bot):
        self.bot = bot
        self.credentials = credentials
        self.channels = self.credentials.CHANNELS

        self.host = "irc.chat.twitch.tv"
        self.port = 6667
        self.ssl = False
        if credentials.CLIENT_ID is None:
            ctx.send("Please set twitchbot client ID with [p]twitchbot botset")
        else:
            self.helix = twitch.Helix(credentials.CLIENT_ID)
            self.messageListener()
            self.run()


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

    @twitchirc.on('CLIENT_CONNECT')
    async def connect(self,channel):
        self.twitchirc.send('PASS', password='oauth:'+self.credentials.CLIENT_OAUTH)
        self.twitchirc.send('NICK', nick=self.credentials.CLIENT_USERNAME.lower())

        # Don't try to join channels until the server has
        # sent the MOTD, or signaled that there's no MOTD.
        done, pending = await asyncio.wait(
            [self.twitchirc.wait("RPL_ENDOFMOTD"),
             self.twitchirc.wait("ERR_NOMOTD")],
            loop=self.twitchirc.loop,
            return_when=asyncio.FIRST_COMPLETED
        )

        # Cancel whichever waiter's event didn't come in.
        for future in pending:
            future.cancel()

        self.twitchirc.send('JOIN', channel=channel)

    @bot.on('PING')
    def keepalive(self, message):
        self.twitchirc.send('PONG', message=message)

    @bot.on('PRIVMSG')
    def message(self, nick, target, message):
        """ Echo all messages """

        # Don't echo ourselves
        if nick == NICK:
            return
        # Respond directly to direct messages
        if target == NICK:
            self.twitchirc.send("PRIVMSG", target=nick, message=message)
        # Channel message
        else:
            self.twitchirc.send("PRIVMSG", target=target, message=message)

    def run(self):
        # This schedules a connection to be created when the bot's event loop
        # is run.  Nothing will happen until the loop starts running to clear
        # the pending coroutines.
        for channel in self.credentials.CHANNELS:
            self.twitchirc.loop.create_task(self.twitchirc.connect())
            # Ctrl + C to quit
            print(
                "Connecting to {} on port {} as {} in channel {}".format(
                   host, port, NICK, CHANNEL))
            self.twitchirc.loop.run_forever()

