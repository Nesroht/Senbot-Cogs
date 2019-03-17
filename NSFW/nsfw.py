import discord
from redbot.core import checks, Config, commands
# Sys
import asyncio
import aiohttp
import time
import random
import json

from NSFW import credentials
from bs4 import BeautifulSoup
from gfycat.client import GfycatClient

import praw
import os
import sys

DEFAULT = {"nsfw_channels": ["133251234164375552"], "invert" : False, "nsfw_msg": True, "last_update": 0,  "ama_boobs": 10548, "ama_ass": 4542}# Red's testing chan. nsfw content off by default.

#API info:
#example: "/boobs/10/20/rank/" - get 20 boobs elements, start from 10th ordered by rank; noise: "/noise/{count=1; sql limit}/",
#example: "/noise/50/" - get 50 random noise elements; model search: "/boobs/model/{model; sql ilike}/",
#example: "/boobs/model/something/" - get all boobs elements, where model name contains "something", ordered by id; author search: "/boobs/author/{author; sql ilike}/",
#example: "/boobs/author/something/" - get all boobs elements, where author name contains "something", ordered by id; get boobs by id: "/boobs/get/{id=0}/",
#example: "/boobs/get/6202/" - get boobs element with id 6202; get boobs count: "/boobs/count/"; get noise count: "/noise/count/"; vote for boobs: "/boobs/vote/{id=0}/{operation=plus;[plus,minus]}/",
#example: "/boobs/vote/6202/minus/" - negative vote for boobs with id 6202; vote for noise: "/noise/vote/{id=0}/{operation=plus;[plus,minus]}/",
#example: "/noise/vote/57/minus/" - negative vote for noise with id 57;

#example: "/butts/10/20/rank/" - get 20 butts elements, start from 10th ordered by rank; noise: "/noise/{count=1; sql limit}/",
#example: "/noise/50/" - get 50 random noise elements; model search: "/butts/model/{model; sql ilike}/",
#example: "/butts/model/something/" - get all butts elements, where model name contains "something", ordered by id; author search: "/butts/author/{author; sql ilike}/",
#example: "/butts/author/something/" - get all butts elements, where author name contains "something", ordered by id; get butts by id: "/butts/get/{id=0}/",
#example: "/butts/get/6202/" - get butts element with id 6202; get butts count: "/butts/count/"; get noise count: "/noise/count/"; vote for butts: "/butts/vote/{id=0}/{operation=plus;[plus,minus]}/",
#example: "/butts/vote/6202/minus/" - negative vote for butts with id 6202; vote for noise: "/noise/vote/{id=0}/{operation=plus;[plus,minus]}/",
#example: "/noise/vote/57/minus/" - negative vote for noise with id 57;

class NSFW(commands.Cog):
    """NSFW cog for Senbot"""

    def __init__(self, bot):
        self.bot = bot
        self.settings = Config.get_conf(self, identifier=69)
        self.credentials = credentials
        default_global = {
            "ama_ass": 0,
            "ama_boobs": 0,
            "last_update": 0
        }
        default_guild = {
            "invert": False,
            "nsfw_channels": [],
            "nsfw_msg": True
        }
        self.settings.register_guild(**default_guild)
        self.settings.register_global(**default_global)
        self._session = aiohttp.ClientSession(loop=self.bot.loop)
        self.reddit = praw.Reddit(client_id=self.credentials.CLIENT_ID, client_secret=self.credentials.CLIENT_SECRET, user_agent=self.credentials.USER_AGENT)
        self.gfyclient = GfycatClient()
        self.gfyclient.client_id = self.credentials.GFYCAT_ID
        self.gfyclient.client_secret = self.credentials.GFYCAT_SECRET

    async def get(self, url):
        async with self._session.get(url) as response:
            rep = await response.json()
            return rep

    def __unload(self):
        asyncio.get_event_loop().create_task(self._session.close())

    @commands.group(name="nsfw")
    async def _nsfw(self, ctx):
        """The nsfw pictures of nature cog."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()
            return

        # Boobs

    @commands.command(no_pm=True)
    async def boobs(self, ctx):
        """Shows some boobs."""
        try:
            rdm = random.randint(0, await self.settings.ama_boobs())
            search = ("http://api.oboobs.ru/boobs/{}".format(rdm))
            result = await self.get(search)
            tmp = random.choice(result)
            boob = "http://media.oboobs.ru/{}".format(tmp["preview"])
        except Exception as e:
            await ctx.send("Error getting results.\n{}".format(e))
            return
        if ctx.channel.is_nsfw():
            emb = discord.Embed(title="Boobs")
            emb.set_image(url=boob)
            await ctx.send(embed=emb)

    # Ass
    @commands.command(no_pm=False)
    async def ass(self, ctx):
        """Shows some ass."""
        try:
            rdm = random.randint(0, await self.settings.ama_ass())
            search = ("http://api.obutts.ru/butts/{}".format(rdm))
            result = await self.get(search)
            tmp = random.choice(result)
            ass = "http://media.obutts.ru/{}".format(tmp["preview"])
        except Exception as e:
            await ctx.send("Error getting results.\n{}".format(e))
            return
        if ctx.channel.is_nsfw():
            emb = discord.Embed(title="Ass")
            emb.set_image(url=ass)
            await ctx.send(embed=emb)

    @checks.admin_or_permissions(administrator=True)
    @_nsfw.command(no_pm=True)
    async def togglensfw(self, ctx):
        """Toggle nswf for this channel on/off.
        Admin/owner restricted."""
        nsfwChan = False
        # Reset nsfw.
        chans = await self.settings.guild(ctx.guild).nsfw_channels()
        for a in chans:
            if a == ctx.message.channel.id:
                nsfwChan = True
                chans.remove(a)
                await self.settings.guild(ctx.guild).nsfw_channels.set(chans)
                await ctx.send("nsfw ON")
                break
        # Set nsfw.
        if not nsfwChan:
            if ctx.message.channel not in chans:
                chans.append(ctx.message.channel.id)
                await self.settings.guild(ctx.guild).nsfw_channels.set(chans)
                await ctx.send("nsfw OFF")

    @checks.admin_or_permissions(administrator=True)
    @_nsfw.command(no_pm=True)
    async def invert(self, ctx):
        """Invert nsfw blacklist to whitelist
        Admin/owner restricted."""
        if not await self.settings.guild(ctx.guild).invert():
            await self.settings.guild(ctx.guild).invert.set(True)
            await ctx.send("The nsfw list for all servers is now: inverted.")
        elif await self.settings.guild(ctx.guild).invert():
            await self.settings.guild(ctx.guild).invert.set(False)
            await ctx.send("The nsfw list for this server is now: default(blacklist)")

    @checks.is_owner()
    @_nsfw.command(hidden=True)
    async def update(self, ctx):
        await ctx.send("Starting update ...")
        await self.boob_knowlegde()
        await ctx.send("Looks done !")

    async def boob_knowlegde(self):
        # KISS
        last_update = await self.settings.last_update()
        now = round(time.time())
        interval = 86400 * 2
        print("Current Time: " + str(now) + " | Last Update: " + str(last_update + interval))
        if now >= last_update + interval:
            await self.settings.last_update.set(now)
        else:
            print("No update needed")
            return

        async def search(url, curr):
            search = ("{}{}".format(url, curr))
            return await self.get(search)

        # Upadate boobs len
        print("Updating amount of boobs...")
        curr_boobs = await self.settings.ama_boobs()
        url = "http://api.oboobs.ru/boobs/"
        done = False
        reachable = curr_boobs
        step = 50
        while not done:
            q = reachable + step
            print("Searching for boobs:", q)
            res = await search(url, q)
            if res != []:
                reachable = q
                res_dc = await search(url, q + 1)
                if res_dc == []:
                    await self.settings.ama_boobs.set(reachable)
                    break
                else:
                    await asyncio.sleep(1)  # Trying to be a bit gentle for the api.
                    continue
            elif res == []:
                step = round(step / 2)
                if step <= 1:
                    await self.settings.ama_boobs.set(curr_boobs)
                    done = True
            await asyncio.sleep(1)
        print("Total amount of boobs:", await self.settings.ama_boobs())

        # Upadate ass len
        print("Updating amount of ass...")
        curr_ass = await self.settings.ama_ass()
        url = "http://api.obutts.ru/butts/"
        done = False
        reachable = curr_ass
        step = 50
        while not done:
            q = reachable + step
            print("Searching for ass:", q)
            res = await search(url, q)
            if res != []:
                reachable = q
                res_dc = await search(url, q + 1)
                if res_dc == []:
                    await self.settings.ama_ass.set(reachable)
                    break
                else:
                    await asyncio.sleep(1)
                    continue
            elif res == []:
                step = round(step / 2)
                if step <= 1:
                    await self.settings.ama_ass.set(curr_ass)
                    done = True
            await asyncio.sleep(1)
        if await self.settings.ama_ass() == 0:
            await self.settings.ama_ass.set(5500)
        print("Total amount of ass:", await self.settings.ama_ass())

    @commands.command()
    @commands.is_nsfw()
    async def yandere(self, ctx):
        """Random Image From Yandere"""
        try:
            query = ("https://yande.re/post/random")
            page = await (await self._session.get(query)).text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="highres").get("href")
            emb = discord.Embed(title="Yandere")
            emb.set_image(url=image)
            await ctx.send(embed=emb)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @commands.command()
    @commands.is_nsfw()
    async def konachan(self, ctx):
        """Random Image From Konachan"""
        try:
            query = ("https://konachan.com/post/random")
            page = await (await self._session.get(query)).text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="highres").get("href")
            emb = discord.Embed(title="Konachan")
            emb.set_image(url=image)
            await ctx.send(embed=emb)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    #@commands.command()
    #@commands.is_nsfw()
    #async def e621(self, ctx):
    #    """Random Image From e621"""
    #    try:
    #        query = ("https://e621.net/post/random")
    #        page = await (await self._session.get(query)).text()
    #        soup = BeautifulSoup(page, 'html.parser')
    #        image = soup.find(id="image").get("src")
    #        emb = discord.Embed(title="e621")
    #        emb.set_image(url=image)
    #        await ctx.send(embed=emb)
    #    except Exception as e:
    #        await ctx.send(f":x: **Error:** `{e}`")

    @commands.command()
    @commands.is_nsfw()
    async def rule34(self, ctx):
        """Random Image From rule34"""#
        try:
            query = ("http://rule34.xxx/index.php?page=post&s=random")
            page = await (await self._session.get(query)).text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="image").get("src")
            emb = discord.Embed(title="Rule34")
            emb.set_image(url=image)
            await ctx.send(embed=emb)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @commands.command()
    @commands.is_nsfw()
    async def danbooru(self, ctx):
        """Random Image From Danbooru"""
        try:
            query = ("http://danbooru.donmai.us/posts/random")
            page = await (await self._session.get(query)).text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="image").get("src")
            emb = discord.Embed(title="Danbooru")
            emb.set_image(url=image)
            await ctx.send(embed=emb)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @commands.command()
    @commands.is_nsfw()
    async def gelbooru(self, ctx):
        """Random Image From Gelbooru"""
        try:
            query = ("http://www.gelbooru.com/index.php?page=post&s=random")
            page = await (await self._session.get(query)).text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="image").get("src")
            emb = discord.Embed(title="Gelbooru")
            emb.set_image(url=image)
            await ctx.send(embed=emb)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @commands.command()
    @commands.is_nsfw()
    async def tbib(self, ctx):
        """Random Image From TBIB"""
        try:
            query = ("http://www.tbib.org/index.php?page=post&s=random")
            page = await (await self._session.get(query)).text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="image").get("src")
            emb = discord.Embed(title="Tbib")
            emb.set_image(url="http:" + image)
            await ctx.send(embed=emb)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @commands.command()
    @commands.is_nsfw()
    async def xbooru(self, ctx):
        """Random Image From Xbooru"""
        try:
            query = ("http://xbooru.com/index.php?page=post&s=random")
            page = await (await self._session.get(query)).text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="image").get("src")
            emb = discord.Embed(title="xBooru")
            emb.set_image(url=image)
            await ctx.send(embed=emb)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @commands.command()
    @commands.is_nsfw()
    async def furrybooru(self, ctx):
        """Random Image From Furrybooru"""
        try:
            query = ("http://furry.booru.org/index.php?page=post&s=random")
            page = await (await self._session.get(query)).text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="image").get("src")
            emb = discord.Embed(title="FurryBooru")
            emb.set_image(url=image)
            await ctx.send(embed=emb)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @commands.command()
    @commands.is_nsfw()
    async def drunkenpumken(self, ctx):
        """Random Image From DrunkenPumken"""
        try:
            query = ("http://drunkenpumken.booru.org/index.php?page=post&s=random")
            page = await (await self._session.get(query)).text()
            soup = BeautifulSoup(page, 'html.parser')
            image = soup.find(id="image").get("src")
            emb = discord.Embed(title="DrunkenPumken")
            emb.set_image(url=image)
            await ctx.send(embed=emb)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    #@commands.command()
    #a#sync def randomtest(self, ctx):
    #    """Random Gif"""
    #    try:
    #        emb = discord.Embed(title="Random Test")
    #        emb.set_image(url="https://media1.tenor.com/images/e0a3715cf354232db50d6bd3476b0576/tenor.gif?itemid=10654993")
    #        await ctx.send(embed=emb)
    #    except Exception as e:
    #        await ctx.send(f":x: **Error:** `{e}`")

    @commands.command()
    async def r(self, ctx, *, subreddit):
        """Random Post from subreddit"""
        posts = self.reddit.subreddit(subreddit).hot(limit=100)
        random_post_number = random.randint(1, 100)
        for i, post in enumerate(posts):
            if i == random_post_number:
                emb = discord.Embed(title=post.title)
                video = 0
                oldurl = post.url
                if oldurl.startswith('https://gfycat'):
                    newurl1, newurl2 = post.url.split('/gfycat.com/')
                    if "-" in newurl2:
                        newurl2 = newurl2.split('-')[0]
                    #print(newurl2)
                    urlList = self.gfyclient.query_gfy(newurl2)
                    gifUrl = urlList["gfyItem"]
                    emb.set_image(url=gifUrl["gifUrl"])
                elif oldurl.startswith('https://imgur') | oldurl.startswith('https://m.imgur'):
                    newurl1, newurl2 = post.url.split('//')
                    #print(newurl1 + newurl2)
                    newurl = newurl1 + "//i."+newurl2+".gif"
                    emb.set_image(url=newurl)
                elif oldurl.startswith('https://i.imgur') & oldurl.endswith('v'):
                    newurl1, newurl2 = post.url.split('//')
                    #print(newurl1 + newurl2)
                    newurl3 = newurl2.split('.gifv')
                    newurl = newurl1 + "//" + newurl3 + ".gif"
                    emb.set_image(url=newurl)
                elif oldurl.startswith('https://youtube') | oldurl.startswith('https://www.youtube') |oldurl.startswith('https://www.pornhub') | oldurl.startswith('https://pornhub') | oldurl.startswith('https://www.reddit'):
                    #newurl = post.url
                    video = 1
                elif oldurl.startswith('https://i.'):
                    emb.set_image(url=oldurl)
                await ctx.send(embed=emb)
                if video == 1:
                    await ctx.send(oldurl)