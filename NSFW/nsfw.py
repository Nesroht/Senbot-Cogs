import discord
from redbot.core import checks, Config, commands
# Sys
import asyncio
import aiohttp
import time
import random
import copy
import json
from urllib.request import urlopen
import requests
import requests.auth
from imgurpython import ImgurClient
from praw.exceptions import ClientException


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
        self.redditdebug = False
        self.r_old_done = False
        self.gfyclient = GfycatClient()
        self.gfyclient.client_id = self.credentials.GFYCAT_ID
        self.gfyclient.client_secret = self.credentials.GFYCAT_SECRET


        #Reddit API access token querying
        self.client_auth = requests.auth.HTTPBasicAuth(credentials.CLIENT_ID, credentials.CLIENT_SECRET)
        self.post_data = {"grant_type": "password", "username": credentials.REDDIT_USERNAME, "password": credentials.REDDIT_PASSWORD}
        self.headers = {"User-Agent": credentials.USER_AGENT}
        response = requests.post("https://www.reddit.com/api/v1/access_token", auth=self.client_auth,
                                 data=self.post_data,
                                 headers=self.headers)
        response_data = response.json()
        self.headers = {"Authorization": response_data["token_type"] + " " + response_data["access_token"],
                        "User-Agent": credentials.USER_AGENT}

        #Imgur api access token querying
        self.iclient_id = self.credentials.ICLIENT_ID
        self.iclient_secret = self.credentials.ICLIENT_SECRET
        self.iclient = ImgurClient(self.iclient_id, self.iclient_secret)
        #self.icredentials = self.iclient.authorize('PIN OBTAINED FROM AUTHORIZATION', 'pin')
        #self.iclient.set_user_auth(self.icredentials['access_token'], self.icredentials['refresh_token'])

    async def get(self, url):
        async with self._session.get(url) as response:
            rep = await response.json()
            return rep

    def __unload(self):
        asyncio.get_event_loop().create_task(self._session.close())

    async def authorize(self):
        response = requests.post("https://www.reddit.com/api/v1/access_token", auth=self.client_auth,
                                 data=self.post_data,
                                 headers=self.headers)
        response_data = response.json()
        self.headers = {"Authorization": response_data["token_type"] + " " + response_data["access_token"],
                        "User-Agent": credentials.USER_AGENT}

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
    async def r(self, ctx, *, subreddit):
        """Random Post from subreddit"""
        try:
            test = self.reddit.subreddit(subreddit).random()
            await self.red(ctx, subreddit=subreddit)
        except ClientException as e:
            if e:
                await self.oldred(ctx, subreddit=subreddit)
                return

    async def redfunc(self, ctx, *, subreddit, oldurl, stickied, over_18, title, selftext, origin):
        #
        #   If redditdebug is active print post url in console
        #
        if self.redditdebug:
            print(oldurl)

        #
        #   Check if post url exists or is stickied, if it is find a new post
        #
        if oldurl is None or stickied:
            await self.red(ctx, subreddit=subreddit)

        #
        #   Check if post is allowed in channel
        #
        if ctx.channel.is_nsfw() == False and over_18 == True:
            await ctx.send("**`r/" + subreddit + " or the random post is not fit for this discord channel!`**")
            if origin == "new":
                return
            else:
                self.r_old_done = True
                return False

        #
        #   Prepare variables for later
        #
        emb = discord.Embed(title="r/" + subreddit, description=title)
        video = 0

        #
        #   Check if url ends with valid image formats, if it does put in embed
        #
        if oldurl.endswith(".gif" or ".jpg" or ".png"):
            emb.set_image(url=oldurl)

        #
        #   Check if url is gfycat, if it is reformat link to work in embed
        #
        elif oldurl.startswith('https://gfycat'):
            newurl1, newurl2 = oldurl.split('/gfycat.com/')
            if "-" in newurl2:
                newurl2 = newurl2.split('-')[0]
            if "/" in newurl2:
                if newurl2[2] == "/":
                    newurl2 = newurl2[2:]
            # print(newurl2)
            urlList = self.gfyclient.query_gfy(newurl2)
            gifUrl = urlList["gfyItem"]
            emb.set_image(url=gifUrl["gifUrl"])

        #
        #   Check if url is Imgur album, if it is post all images in album
        #
        elif "imgur.com/a" in oldurl:
            if "imgur.com/a" in oldurl:
                dump, album_id = oldurl.split("/a/")
                albumlist = self.iclient.get_album_images(album_id)
                count = 1
                for pic in albumlist:
                    emb = discord.Embed(title="r/" + subreddit,
                                        description=post.get("title") + " " + str(count) + "/" + str(
                                            len(albumlist)))
                    emb.set_image(url=pic.link)
                    count += 1
                    await ctx.send(embed=emb)
                if origin == "old":
                    self.r_old_one = True
                    return False
                return
            elif "imgur.com/album" in oldurl:
                dump, album_id = oldurl.split("/album/")
                albumlist = self.iclient.get_album_images(album_id)
                count = 1
                for pic in albumlist:
                    emb = discord.Embed(title="r/" + subreddit,
                                        description=post.get("title") + " " + str(count) + "/" + str(
                                            len(albumlist)))
                    emb.set_image(url=pic.link)
                    count += 1
                    await ctx.send(embed=emb)
                if origin == "old":
                    self.r_old_one = True
                    return False
                return

        #
        #   Check if url is imgur, if it is reformat to .gif to work in embed
        #
        elif oldurl.startswith('https://imgur') or oldurl.startswith('https://m.imgur'):
            newurl1, newurl2 = oldurl.split('//')
            # print(newurl1 + newurl2)
            newurl = newurl1 + "//i." + newurl2 + ".gif"
            emb.set_image(url=newurl)

        #
        #   Checks if url is imgur, if it is changes ending to work with embed
        #
        elif oldurl.startswith('https://i.imgur') and oldurl.endswith('v'):
            video = 1

        #
        #   Checks if url is .gifv, if it is post out of embed
        #
        elif subreddit in oldurl:
            if "i.redd.it" in selftext:
                newurl1, newurl2 = oldurl.split("https://")
                newurl = "https://" + newurl2
                emb.set_image(url=newurl)
            else:
                if origin == "new":
                    await self.red(ctx, subreddit=subreddit)
                    return
                else:
                    self.r_old_done = False
                    return False

        #
        #   Checks if url is various video/audio sites, if it is post out of embed
        #
        elif oldurl.startswith('https://youtube') or oldurl.startswith(
                'https://youtu.be') or oldurl.startswith('https://www.youtube') or oldurl.startswith(
            'https://www.pornhub') or oldurl.startswith('https://pornhub') or oldurl.startswith(
            'https://soundcloud') or oldurl.startswith(
            'https://www.soundcloud'):
            video = 1

        #
        #   Catch check, if url starts with i. assume it is a valid image link and add it to embed
        #
        elif oldurl.startswith('https://i.'):
            emb.set_image(url=oldurl)

        #
        #   If none of the cases above passed, try another post
        #
        else:
            if origin == "new":
                await self.red(ctx, subreddit=subreddit)
                return
            else:
                self.r_old_done = False
                return False
        await ctx.send(embed=emb)

        #
        #   Variable check for if url should be passed outside of embed
        #
        if video == 1:
            await ctx.send(oldurl)
        if origin == "old":
            self.r_old_done = True
            return False
        return

    async def oldred(self,ctx,*,subreddit):
        try:
            #
            #   Initiate ListingGenerator for given subreddit with limit, Iterate over each post until given random number reached
            #
            #print("old")
            posts = self.reddit.subreddit(subreddit).hot(limit=100)
            random_post_number = random.randint(0, 100)
            self.r_old_done = False
            for i, post in enumerate(posts):
                if i == random_post_number:
                    check_if_done = True
                    while check_if_done:
                        check_if_done = await redfunc(ctx, subreddit=subreddit, oldurl=post.url, stickied=post.stickied, over_18=post.over_18, title=post.title, selftext=post.selftext, origin="old")
                        if check_if_done is False:
                            break
                    if self.r_old_done is False:
                        random_post_number += 1
                        continue
                    else:
                        break
        except Exception as e:

            #
            #   Is redditdebug false? Consider all errors as reddit not existing
            #
            if self.redditdebug is False:
                await ctx.send("**`Can't find subreddit " + subreddit + "`**")

            #
            #   Is redditdebug true? print error to console
            #
            else:
                print(e)

    async def red(self, ctx, *, subreddit):
        try:
            #
            #   Request random post json from reddit
            #
            print("new")
            query = requests.get("https://oauth.reddit.com/r/" + subreddit + "/random.json", headers=self.headers)
            #print(query.status_code)

            #
            #   If query responds with 401, reauthorize client
            #
            if query.status_code == 401:
                self.authorize(self)
                query = requests.get("https://oauth.reddit.com/r/" + subreddit + "/random.json", headers=self.headers)

            #
            #   Make sure to parse query as json, check if json is instance of list, if it is get first instance in list
            #
            postin = query.json()
            if isinstance(postin, list):
                postin = postin[0]

            #
            #   Parse through json to easily get variables needed from post
            #
            postjson = postin.get("data")
            postjson = postjson.get("children")
            postjson = postjson[0]
            post = postjson.get("data")
            # print(i)

            await redfunc(ctx, subreddit=subreddit, oldurl=post.get("url"), stickied=post.get("stickied"), over_18=post.get("over_18"), title=post.get("title"), selftext=post.get("selftext"), origin="new")
        except Exception as e:
            if self.redditdebug is False:
                await ctx.send("**`Can't find subreddit " + subreddit + "`**")
            else:
                print(e)


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
            random_number = random.randint(0,100)
            if random_number < 50:
                query = ("http://rule34.xxx/index.php?page=post&s=random")
                page = await (await self._session.get(query)).text()
                soup = BeautifulSoup(page, 'html.parser')
                image = soup.find(id="image").get("src")
                emb = discord.Embed(title="Rule34")
                emb.set_image(url=image)
                await ctx.send(embed=emb)
            else:
                await self.red(ctx,subreddit="rule34")

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
    async def rdebug(self, ctx):
        if self.redditdebug is False:
            self.redditdebug = True
            await ctx.send("Enabled reddit debug output in console!")
        else:
            self.redditdebug = False
            await ctx.send("Disabled reddit debug output in console!")

    @commands.command()
    async def rtest(self, ctx, *, subreddit):
        query = requests.get("https://oauth.reddit.com/r/" + subreddit + "/random.json", headers=self.headers)
        # print(query.status_code)
        if query.status_code == 401:
            self.authorize(self)
            query = requests.get("https://oauth.reddit.com/r/" + subreddit + "/random.json", headers=self.headers)
        postin = query.json()
        if postin is list:
            postin = postin[0]
        postjson = postin.get("data")
        postjson = postjson.get("children")
        postjson = postjson[0]
        post = postjson.get("data")
        # print(i)
        if self.redditdebug:
            print(post.get("url"))
        if post.get("url") is None or post.get("stickied"):
            r(self, ctx, subreddit)
        # print("NSFW Channel?: "+ str(ctx.channel.is_nsfw()) + " | NSFW Post?: "+str(post.over_18))
        if ctx.channel.is_nsfw() == False and post.get("over_18") == True:
            await ctx.send("**`r/" + subreddit + " or the random post is not fit for this discord channel!`**")
            return
        emb = discord.Embed(title="r/" + subreddit, description=post.get("title"))
        video = 0
        oldurl = post.get("url")
        if oldurl.endswith(".gif" or ".jpg" or ".png"):
            emb.set_image(url=oldurl)
        elif oldurl.startswith('https://gfycat'):
            newurl1, newurl2 = post.get("url").split('/gfycat.com/')
            if "-" in newurl2:
                newurl2 = newurl2.split('-')[0]
            if "/" in newurl2:
                if newurl2[2] == "/":
                    newurl2 = newurl2[2:]
            # print(newurl2)
            urlList = self.gfyclient.query_gfy(newurl2)
            gifUrl = urlList["gfyItem"]
            emb.set_image(url=gifUrl["gifUrl"])
        elif "imgur.com/a" in oldurl:
            if "imgur.com/a" in oldurl:
                dump, album_id = oldurl.split("/a/")
                albumlist = self.iclient.get_album_images(album_id)
                count = 1
                for pic in albumlist:
                    emb = discord.Embed(title="r/" + subreddit, description=post.get("title") + " " + str(count) + "/" + str(len(albumlist)))
                    emb.set_image(url=pic.link)
                    count += 1
                    await ctx.send(embed=emb)
                return
            if "imgur.com/album" in oldurl:
                dump, album_id = oldurl.split("/album/")
                albumlist = self.iclient.get_album_images(album_id)
                count = 1
                for pic in albumlist:
                    emb = discord.Embed(title="r/" + subreddit, description=post.get("title") + " " + str(count) + "/" + str(len(albumlist)))
                    emb.set_image(url=pic.link)
                    count += 1
                    await ctx.send(embed=emb)
                return
        elif oldurl.startswith('https://imgur') or oldurl.startswith('https://m.imgur'):
            newurl1, newurl2 = post.get("url").split('//')
            # print(newurl1 + newurl2)
            newurl = newurl1 + "//i." + newurl2 + ".gif"
            emb.set_image(url=newurl)
        elif oldurl.startswith('https://i.imgur') and oldurl.endswith('v'):
            video = 1
        elif subreddit in oldurl:
            if "i.redd.it" in post.get("selftext"):
                newurl1, newurl2 = oldurl.split("https://")
                newurl = "https://" + newurl2
                emb.set_image(url=newurl)
            else:
                await self.red(ctx, subreddit=subreddit)
                return
        elif oldurl.startswith('https://youtube') or oldurl.startswith(
                'https://youtu.be') or oldurl.startswith('https://www.youtube') or oldurl.startswith(
            'https://www.pornhub') or oldurl.startswith('https://pornhub') or oldurl.startswith(
            'https://soundcloud') or oldurl.startswith(
            'https://www.soundcloud'):
            # newurl = post.get("url")
            video = 1
        elif oldurl.startswith('https://i.'):
            emb.set_image(url=oldurl)
        else:
            await self.red(ctx, subreddit=subreddit)
            return
        await ctx.send(embed=emb)
        if video == 1:
            await ctx.send(oldurl)
        return