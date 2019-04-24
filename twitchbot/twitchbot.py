import discord
from redbot.core import checks, Config, commands

import asyncio
import socket
import json

from redbot.core import bank

import re
import time
import requests

import select

class Twitchbot(commands.Cog):
    """Twitchbot in a cog for Senbot"""

    def __init__(self, bot):
        self.bot = bot
        self.settings = Config.get_conf(self, identifier=69)
        with open("/home/senbot/.local/share/Red-DiscordBot/cogs/CogManager/cogs/twitchbot/credentials.json") as f:
            self.credentials = json.load(f)
        with open("/home/senbot/.local/share/Red-DiscordBot/cogs/CogManager/cogs/twitchbot/balance.json") as f:
            self.bal = json.load(f)
        self.token = self.credentials["CLIENT_OAUTH"]
        self.nickname = self.credentials["CLIENT_USERNAME"]
        self.server = "irc.chat.twitch.tv"
        self.channelviewers = {"CHANNEL":{"nesroht":{}, "senrohbot": {}}}
        self.databuffer = []

        #self.userlist = self.credentials.USERS

        self.CHECK_DELAY = 1
        self.port = 6667
        self.sock = {}
        self.task = {}

        self.currency = self.bal["CHANNEL"]

        self.cooldowns = {"!join": {"nesroht": 0},"!bal": {"nesroht": 0}, "!discordlink": {"nesroht": 0}, "!discord": {"nesroht": 0}, "!setcurrency": {"nesroht": 0}}

        if self.credentials["CLIENT_ID"] is None:
            ctx.send("Please set twitchbot client ID with [p]twitchbot botset")
        else:
            for channel in self.credentials["CHANNEL"]:
                #print(channel)
                self.sock[channel] = socket.socket()
                self.task[channel] = self.bot.loop.create_task(self.irc_check(channel))

    def __unload(self):
        for channel in self.credentials["CHANNEL"]:
            self.task[channel].cancel()
            self.sock[channel].close()


    @commands.command()
    async def test(self, ctx, channel,*, message):
        #print(channel + " " + message)
        allowed = False
        if credentials["CLIENT_ID"] is None:
            await ctx.send("Please set twitchbot client ID with [p]twitchbot botset")
        else:
            for testchannel in self.credentials["CHANNEL"]:
                if channel == testchannel:
                    await ctx.send("Testing connection to twitch")
                    self.sock[channel].send(f"PRIVMSG #{channel} :{message}\r\n".encode("utf-8"))
                    allowed = True
            if allowed is False:
                await ctx.send(f"Can\'t test connection to {channel} because not connected to it!")

    @commands.command()
    async def twitchlink(self, ctx, twitchuser):
        found_user = 0
        balance = await bank.get_balance(ctx.author)
        if len(self.credentials["USERS"]) >= 1:
            for i in range(0, len(self.credentials["USERS"])):
                if self.credentials["USERS"][i][1] == ctx.author.id:
                    found_user = i+1

        if found_user>=1:
            self.credentials["USERS"][found_user-1] = [twitchuser.capitalize(), ctx.author.id, balance]
            await ctx.send("Successfully updated your twitch user to " + twitchuser.capitalize())
        else:
            self.credentials["USERS"].append([twitchuser.capitalize(), ctx.author.id, balance])
            #print(str(self.credentials["USERS"]))
            await ctx.send("Successfully linked your discord id to the twitch user "+twitchuser.capitalize())
        with open('/home/senbot/.local/share/Red-DiscordBot/cogs/CogManager/cogs/twitchbot/credentials.json', 'w') as f:
            json.dump(self.credentials, f, ensure_ascii=False, indent=4)


    @commands.group(name="twitchbot")
    async def _twitchbot(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help()
            return

    @_twitchbot.command()
    async def botset(self, ctx, *, client_id, client_username, client_oauth):
        self.credentials["CLIENT_USERNAME"] = client_username
        self.credentials["CLIENT_OAUTH"] = client_oauth
        self.credentials["CLIENT_ID"] = client_id
        with open('/home/senbot/.local/share/Red-DiscordBot/cogs/CogManager/cogs/twitchbot/credentials.json', 'w') as f:
            json.dump(self.credentials, f, ensure_ascii=False, indent=4)

    async def check_bal(self, sender, channel):
        balance = 0
        balancefound = False
        if channel in self.currency:
            currency = self.currency[channel]
        else:
            currency = self.currency["default"]

        for i in range(0, len(self.credentials["USERS"])):
            if self.credentials["USERS"][i][0] == sender:
                for guild in self.bot.guilds:
                    if guild.get_member(self.credentials["USERS"][i][1]):
                        user_found = guild.get_member(self.credentials["USERS"][i][1])
                        found_user = True
                        break
                if found_user:
                    self.credentials["USERS"][i][2] = await bank.get_balance(user_found)
                    with open('/home/senbot/.local/share/Red-DiscordBot/cogs/CogManager/cogs/twitchbot/credentials.json', 'w') as f:
                        json.dump(self.credentials, f, ensure_ascii=False, indent=4)
                print("DONE")
                balance = self.credentials["USERS"][i][2]
                balancefound = True
                break
        if balancefound:
            self.sock[channel].send(f"PRIVMSG #{channel} :{sender}\'s balance is {balance} {currency}\r\n".encode("utf-8"))
        else:
            if sender in self.bal["USERS"]:
                balance = self.bal["USERS"][sender]
                self.sock[channel].send(f"PRIVMSG #{channel} :{sender}\'s balance is {balance} {currency}\r\n".encode("utf-8"))
            else:
                self.bal["USERS"].update({sender: 100})
                with open('/home/senbot/.local/share/Red-DiscordBot/cogs/CogManager/cogs/twitchbot/balance.json','w') as f:
                    json.dump(self.bal, f, ensure_ascii=False, indent=4)
                balance = self.bal["USERS"][sender]
                self.sock[channel].send(f"PRIVMSG #{channel} :@{sender}, you have {balance} {currency}\r\n".encode("utf-8"))


    async def irc_check(self, channel):
        self.sock[channel].connect((self.server, self.port))
        self.sock[channel].send(f"PASS {self.token}\r\n".encode('utf-8'))
        self.sock[channel].send(f"NICK {self.nickname}\r\n".encode('utf-8'))
        resp = self.sock[channel].recv(2048).decode("utf-8")
        print(resp)
        self.sock[channel].send(f"JOIN #{channel}\r\n".encode('utf-8'))
        resp = self.sock[channel].recv(2048).decode("utf-8")
        print(resp)
        #self.sock[channel].send(f"PRIVMSG #{channel} :Successfully connected to chat! <3\r\n".encode("utf-8"))
        while True:
            #print("no")
            try:
                ready = select.select([self.sock[channel]],[],[],1)
                if ready[0]:
                    #print("yes")
                    r = requests.get(f"http://tmi.twitch.tv/group/user/{channel}/chatters")
                    self.channelviewers["CHANNEL"][channel].update(r.json())
                    senderdata = self.sock[channel].recv(2048).decode("utf-8")  # gets output from IRC server
                    #print(senderdata)
                    if senderdata == "PING :tmi.twitch.tv\r\n":
                        self.sock[channel].send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                        #print(f"Sent pong response on {channel}")
                        continue
                    sender, dump = senderdata.split("!", 1)
                    now = round(time.time())
                    if "!join\r\n" in senderdata:
                        if channel != "1uptaco":
                            continue
                        sender, dump = senderdata.split("!", 1)
                        finish = sender[1:].capitalize()
                        if sender[1:] in self.cooldowns["!join"]:
                            if self.cooldowns["!join"][sender[1:]] > now:
                                cooldowntime = self.cooldowns["!join"][sender[1:]]
                                self.sock[channel].send(f"PRIVMSG #{channel} :That command is on cooldown for another {cooldowntime-now} seconds {finish}!\r\n".encode("utf-8"))
                                await asyncio.sleep(self.CHECK_DELAY)
                                continue
                        if sender[1:] != self.channelviewers["CHANNEL"][channel]["chatters"]["broadcaster"][0]:
                            if sender[1:] in self.channelviewers["CHANNEL"][channel]["chatters"]["moderators"]:
                                print("success")
                            else:
                                self.sock[channel].send(f"PRIVMSG #{channel} :Only moderators can use this command.\r\n".encode("utf-8"))
                                continue
                        self.sock[channel].send(f"PRIVMSG #{channel} :If you want to join this RP Ark server you have to go apply at: http://westerosrp.net/apply/\r\n".encode("utf-8"))
                        self.cooldowns["!join"].update({sender[1:]: now + 30})

                    if "!bal\r\n" in senderdata:
                        #print("Baltest")
                        sender, dump = senderdata.split("!", 1)
                        finish = sender[1:].capitalize()
                        if sender[1:] in self.cooldowns["!bal"]:
                            if self.cooldowns["!bal"][sender[1:]] > now:
                                cooldowntime = self.cooldowns["!bal"][sender[1:]]
                                self.sock[channel].send(f"PRIVMSG #{channel} :That command is on cooldown for another {cooldowntime-now} seconds {finish}!\r\n".encode("utf-8"))
                                await asyncio.sleep(self.CHECK_DELAY)
                                continue
                        else:
                            self.cooldowns["!bal"].update({sender[1:]: now})
                        await self.check_bal(finish, channel)
                        self.cooldowns["!bal"].update({sender[1:]: now + 30})
                    elif "!discord\r\n" in senderdata:
                        sender, dump = senderdata.split("!", 1)
                        finish = sender[1:].capitalize()
                        if sender[1:] in self.cooldowns["!discord"]:
                            if self.cooldowns["!discord"][sender[1:]] > now:
                                cooldowntime = self.cooldowns["!discord"][sender[1:]]
                                self.sock[channel].send(f"PRIVMSG #{channel} :That command is on cooldown for another {cooldowntime-now} seconds {finish}!\r\n".encode("utf-8"))
                                await asyncio.sleep(self.CHECK_DELAY)
                                continue
                        else:
                            self.cooldowns["!discord"].update({sender[1:]: now})
                        self.sock[channel].send(f"PRIVMSG #{channel} :Hey {finish}, Join our discord channel at: https://discord.gg/nqNDjts I have more commands there! ;)\r\n".encode("utf-8"))
                        self.cooldowns["!discord"].update({sender[1:]: now + 30})
                    elif "!test" in senderdata:
                        print("Success")
                        self.sock[channel].send(f"PRIVMSG #{channel} :Test successful!\r\n".encode("utf-8"))

                    elif "!setcurrency" in senderdata:
                        if sender[1:] in self.cooldowns["!setcurrency"]:
                            if self.cooldowns["!setcurrency"][sender[1:]] > now:
                                cooldowntime = self.cooldowns["!setcurrency"][sender[1:]]
                                self.sock[channel].send(f"PRIVMSG #{channel} :That command is on cooldown for another {cooldowntime-now} seconds {finish}!\r\n".encode("utf-8"))
                                await asyncio.sleep(self.CHECK_DELAY)
                                continue
                        else:
                            self.cooldowns["!setcurrency"].update({sender[1:]: now})
                        print(self.channelviewers["CHANNEL"][channel]["chatters"]["broadcaster"][0])
                        if sender[1:] != self.channelviewers["CHANNEL"][channel]["chatters"]["broadcaster"][0] or sender[1:] != self.channelviewers["CHANNEL"][channel]["chatters"]["moderator"][0]:
                            self.sock[channel].send(f"PRIVMSG #{channel} :Only the streamer can use this command.\r\n".encode("utf-8"))
                            continue
                        if re.search(r"!setcurrency +(\w|\#)+", senderdata, re.IGNORECASE) is not None:
                            print("test")
                            dump, arguments = senderdata.split("!setcurrency ")
                            arguments, dump = arguments.split("\r\n")
                            if channel in self.currency:
                                print("test1")
                                self.bal["CHANNEL"][channel] = arguments
                                print("test2")
                                with open('/home/senbot/.local/share/Red-DiscordBot/cogs/CogManager/cogs/twitchbot/balance.json', 'w') as f:
                                    json.dump(self.bal, f, ensure_ascii=False, indent=4)
                                print("test3")
                                self.currency[channel] = self.bal["CHANNEL"][channel]
                                print("test4")
                                self.sock[channel].send(f"PRIVMSG #{channel} :Set this channels currency name to {self.currency[channel]}\r\n".encode("utf-8"))
                                print("done")
                            else:
                                print("test1")
                                self.bal["CHANNEL"].update({channel: arguments})
                                print("test2")
                                with open('/home/senbot/.local/share/Red-DiscordBot/cogs/CogManager/cogs/twitchbot/balance.json', 'w') as f:
                                    json.dump(self.bal, f, ensure_ascii=False, indent=4)
                                print("test3")
                                self.currency.update({channel: self.bal["CHANNEL"][channel]})
                                print("test4")
                                self.sock[channel].send(f"PRIVMSG #{channel} :Set this channels currency name to {self.currency[channel]}\r\n".encode("utf-8"))
                                print("done")
                        else:
                            defaultcurrency = self.bal["CHANNEL"]["default"]
                            self.sock[channel].send(f"PRIVMSG #{channel} :Add the name for the currency as an argument. Default is {defaultcurrency}\r\n".encode("utf-8"))
                        self.cooldowns["!discord"].update({sender[1:]: now + 30})
                    elif "!discordlink" in senderdata:
                        if re.search(r"!discordlink +(\w|\#)+", senderdata, re.IGNORECASE) is not None:
                            dump, arguments = senderdata.split("!discordlink ")
                            arguments, dump = arguments.split("\r\n")
                            sender, dump = senderdata.split("!", 1)
                            finish = sender[1:].capitalize()
                            if sender[1:] in self.cooldowns["!discordlink"]:
                                if self.cooldowns["!discordlink"][sender[1:]] > now:
                                    cooldowntime = self.cooldowns["!discordlink"][sender[1:]]
                                    self.sock[channel].send(f"PRIVMSG #{channel} :That command is on cooldown for another {cooldowntime - now} seconds {finish}!\r\n".encode("utf-8"))
                                    await asyncio.sleep(self.CHECK_DELAY)
                                    continue
                            else:
                                self.cooldowns["!discordlink"].update({sender[1:]: now})
                            try:
                                arguments = int(arguments)
                                #print(arguments)
                                found_user = False
                                user_found = None
                                #print(str(self.bot.guilds))
                                for guild in self.bot.guilds:
                                    if guild.get_member(arguments):
                                        user_found = guild.get_member(arguments)
                                        found_user = True
                                        break
                                if found_user:
                                    balance = await bank.get_balance(user_found)
                                    found_in_config = 0
                                    self.sock[channel].send(f"PRIVMSG #{channel} :Set your linked discord user to {user_found.name}#{user_found.discriminator}\r\n".encode("utf-8"))
                                    if len(self.credentials["USERS"]) >= 1:
                                        for i in range(0, len(self.credentials["USERS"])):
                                            if self.credentials["USERS"][i][0] == finish:
                                                found_in_config = i + 1
                                    if found_in_config >= 1:
                                        self.credentials["USERS"][found_in_config - 1] = [finish, user_found.id, balance]
                                    else:
                                        self.credentials["USERS"].append([finish, user_found.id, balance])
                                    with open('/home/senbot/.local/share/Red-DiscordBot/cogs/CogManager/cogs/twitchbot/credentials.json', 'w') as f:
                                        json.dump(self.credentials, f, ensure_ascii=False, indent=4)
                                else:
                                    self.sock[channel].send(f"PRIVMSG #{channel} :/w {sender[1:]} Can\'t link your twitch account to that discord user as its not in a discord server i am in! :(\r\n".encode("utf-8"))
                            except ValueError:
                                #print(arguments)
                                if "#" in arguments:
                                    name, discr = arguments.split("#")
                                    found_user = False
                                    user_found = self.bot.user
                                    for guild in self.bot.guilds:
                                        for user in guild.members:
                                            if name == user.name:
                                                if discr == user.discriminator:
                                                    user_found = user
                                                    found_user = True
                                                    break
                                        if found_user:
                                            break
                                    if found_user:
                                        balance = await bank.get_balance(user_found)
                                        found_in_config = 0
                                        self.sock[channel].send(f"PRIVMSG #{channel} :/w {sender[1:]} Set your linked discord user to {user_found.name}#{user_found.discriminator}\r\n".encode("utf-8"))
                                        if len(self.credentials["USERS"]) >= 1:
                                            for i in range(0, len(self.credentials["USERS"])):
                                                if self.credentials["USERS"][i][0] == finish:
                                                    found_in_config = i + 1
                                                    break
                                        if found_in_config >= 1:
                                            self.credentials["USERS"][found_in_config - 1] = [finish, user_found.id, balance]
                                        else:
                                            self.credentials["USERS"].append([finish, user_found.id, balance])
                                        with open('/home/senbot/.local/share/Red-DiscordBot/cogs/CogManager/cogs/twitchbot/credentials.json', 'w') as f:
                                            json.dump(self.credentials, f, ensure_ascii=False, indent=4)
                                    else:
                                        self.sock[channel].send(f"PRIVMSG #{channel} :/w {sender[1:]} Can\'t link your twitch account to that discord user as its not in a discord server i am in! :(\r\n".encode("utf-8"))
                                else:
                                    self.sock[channel].send(f"PRIVMSG #{channel} :/w {sender[1:]} Thats not a valid user {finish}, give me the client id which is all numbers or the name with number after #!\r\n".encode("utf-8"))
                            self.cooldowns["!discordlink"].update({sender[1:]: now + 30})
                        else:
                            sender, dump = senderdata.split("!", 1)
                            finish = sender[1:].capitalize()
                            if self.cooldowns["!discordlink"]:
                                if self.cooldowns["!discordlink"][sender[1:]] > now:
                                    cooldowntime = self.cooldowns["!discordlink"][sender[1:]]
                                    self.sock[channel].send(f"PRIVMSG #{channel} :That command is on cooldown for another {cooldowntime - now} seconds {finish}!\r\n".encode("utf-8"))
                                    await asyncio.sleep(self.CHECK_DELAY)
                                    continue
                            self.sock[channel].send(f"PRIVMSG #{channel} :!discordlink lets you link your discord user to your twitch name {finish}, add your discord id or your discord name#number as an argument!\r\n".encode("utf-8"))
                            self.cooldowns["!discordlink"].update({sender[1:]: now + 30})
                    await asyncio.sleep(self.CHECK_DELAY)
                    continue
                else:
                    await asyncio.sleep(self.CHECK_DELAY)
            except asyncio.CancelledError:
                pass
            await asyncio.sleep(self.CHECK_DELAY)
