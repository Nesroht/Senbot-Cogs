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


from reddit import credentials
from gfycat.client import GfycatClient

import praw
import os
import sys

class Reddit(commands.Cog):
    """Reddit cog for Senbot"""

    def __init__(self, bot):
        self.bot = bot
        self.credentials = credentials
        self._session = aiohttp.ClientSession(loop=self.bot.loop)
        self.reddit = praw.Reddit(client_id=self.credentials.CLIENT_ID, client_secret=self.credentials.CLIENT_SECRET, user_agent=self.credentials.USER_AGENT)
        self.redditdebug = False
        self.r_old_done = False
        self.alimit = 5
        self.randatt = False

        self.gfyclient = GfycatClient()
        self.gfyclient.client_id = self.credentials.GFYCAT_ID
        self.gfyclient.client_secret = self.credentials.GFYCAT_SECRET


        #reddit API access token querying
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
        #self.icredentials = self.iclient.authorize("PIN OBTAINED FROM AUTHORIZATION", "pin")
        #self.iclient.set_user_auth(self.icredentials["access_token"], self.icredentials["refresh_token"])

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

    @commands.group(name="reddit")
    async def _reddit(self, ctx):
        """reddit cog settings and things"""
        pass


    @commands.command()
    async def r(self, ctx, *, subreddit):
        """Random Post from subreddit"""
        self.randatt = False
        await self.redditcommand(ctx, subreddit=subreddit)


    async def redditcommand(self, ctx, *, subreddit):
        try:
            test = self.reddit.subreddit(subreddit).random()
            await self.newred(ctx, subreddit=subreddit)
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
        if (oldurl is "") or (oldurl is stickied):
            if origin == "new":
                await self.newred(ctx, subreddit=subreddit)
                return
            else:
                self.r_old_done = True
                return False

        #
        #   Check if post is allowed in channel
        #
        if ctx.guild:
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
        if ((".gif" in oldurl) or (".jpg" in oldurl) or (".png" in oldurl)) and ".gifv" not in oldurl:
            #await ctx.send("Contains .gif, .jpg or .png")
            if "?" in oldurl:
                newurl, dump = oldurl.split("?")
                if "_" in newurl:
                    newurl2, dump2 = newurl.split("_")
                    emb.set_image(url=newurl2 + ".gif")
                else:
                    emb.set_image(url=newurl)
            else:
                emb.set_image(url=oldurl)

        elif (".mp4") in oldurl and "imgur.com" in oldurl:
            newurl, dump = oldurl.split(".mp")
            video = 1
            oldurl = newurl + ".gifv"

        #
        #   Check if url is gfycat, if it is reformat link to work in embed, Embeds dont support Gfycat gifs properly, so commented out working code
        #
        elif oldurl.startswith("https://gfycat"):
            #newurl1, newurl2 = oldurl.rsplit("/", 1)
            #if "-" in newurl2:
            #    newurl2 = newurl2.split("-")[0]
            #if "/" in newurl2:
            #    if newurl2[2] == "/":
            #        newurl2 = newurl2[2:]
            # print(newurl2)
            #urlList = self.gfyclient.query_gfy(newurl2)
            #gifUrl = urlList["gfyItem"]
            #emb.set_image(url=gifUrl["gifUrl"])
            video = 1

        #
        #   Check if url is Imgur album, if it is post all images in album
        #
        elif ("imgur.com/a/" in oldurl) or ("imgur.com/album/" in oldurl):
            if "imgur.com/a/" in oldurl:
                dump, album_id = oldurl.split("/a/")
            elif "imgur.com/album/" in oldurl:
                dump, album_id = oldurl.split("/album/")
            albumlist = self.iclient.get_album_images(album_id)
            size = len(albumlist)
            random_count = random.randint(0,size)
            if len(albumlist)<= self.alimit:
                random_count = 0
            elif random_count >= size-self.alimit and random_count >= self.alimit:
                random_count = size-self.alimit
            orig_rand = random_count
            count = 1
            for i, pic in enumerate(albumlist):
                if i == random_count:
                    if count <= self.alimit:
                        emb = discord.Embed(title="r/" + subreddit,
                                            description=title + " " + str(count+orig_rand) + "/" + str(
                                                size))
                        if ".gifv" in pic.link:
                            await ctx.send(embed=emb)
                            await ctx.send(pic.link)
                        else:
                            emb.set_image(url=pic.link)
                            await ctx.send(embed=emb)
                        count += 1
                        random_count += 1
            if origin == "old":
                self.r_old_done = True
                return False
            return

        elif ("imgur.com/gallery/" in oldurl) or ("imgur.com/g/" in oldurl):
            randcheck = self.randatt
            if randcheck is True:
                await self.randomfunc(ctx)
                self.r_old_done = True
                return False
            elif origin == "new":
                await self.newred(ctx, subreddit=subreddit)
                return
            else:
                self.r_old_done = False
                return False

        #
        #   Check if url is imgur, if it is reformat to .gif to work in embed
        #
        elif ("https://imgur" in oldurl) or ("https://m.imgur" in oldurl):
            newurl1, newurl2 = oldurl.split("//")
            # print(newurl1 + newurl2)
            if ".gifv" in newurl2:
                oldurl = newurl1 + "//i." + newurl2
                video = 1
            elif (".gif" in newurl2) or (".jpg" in newurl2) or (".png" in newurl2):
                newurl = newurl1 + "//i." + newurl2
                emb.set_image(url=newurl)
            else:
                if "m.imgur" in oldurl:
                    newurl = newurl1 + "//"+newurl2 + ".gif"
                else:
                    newurl = newurl1 + "//i." + newurl2 + ".gif"
                emb.set_image(url=newurl)

        #
        #   Checks if url is .gifv, if it is post out of embed
        #
        elif oldurl.startswith("https://i.imgur") and oldurl.endswith("v"):
            video = 1

        #
        #
        #
        elif (subreddit in oldurl) and (subreddit + ".com" not in oldurl):
            if "i.redd.it" in selftext:
                newurl1, newurl2 = oldurl.split("https://")
                newurl = "https://" + newurl2
                emb.set_image(url=newurl)
            else:
                randcheck = self.randatt
                if randcheck is True:
                    await self.randomfunc(ctx)
                    self.r_old_done = True
                    return False
                elif origin == "new":
                    await self.newred(ctx, subreddit=subreddit)
                    return
                else:
                    self.r_old_done = False
                    return False

        #
        #   Checks if url is various video/audio sites, if it is post out of embed
        #
        elif oldurl.startswith("https://youtube") or oldurl.startswith(
                "https://youtu.be") or oldurl.startswith("https://www.youtube") or oldurl.startswith(
            "https://www.pornhub") or oldurl.startswith("https://pornhub") or oldurl.startswith(
            "https://soundcloud") or oldurl.startswith(
            "https://www.soundcloud"):
            video = 1

        #
        #   Catch check, if url starts with i. assume it is a valid image link and add it to embed
        #
        elif oldurl.startswith("https://i."):
            emb.set_image(url=oldurl)

        #
        #   If none of the cases above passed, try another post
        #
        else:
            randcheck = self.randatt
            if randcheck is True:
                await self.randomfunc(ctx)
                self.r_old_done = True
                return False
            elif origin == "new":
                await self.newred(ctx, subreddit=subreddit)
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
            if self.redditdebug:
                print("old")
            posts = self.reddit.subreddit(subreddit).hot(limit=100)
            random_post_number = random.randint(0, 100)
            self.r_old_done = False
            for i, post in enumerate(posts):
                if i == random_post_number:
                    check_if_done = True
                    while check_if_done:
                        check_if_done = await self.redfunc(ctx, subreddit=subreddit, oldurl=post.url, stickied=post.stickied, over_18=post.over_18, title=post.title, selftext=post.selftext, origin="old")
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

    async def newred(self, ctx, *, subreddit):
        try:
            #
            #   Pull random post from given subreddit and pass it on to redfunc()
            #
            if self.redditdebug:
                print("newer")
            post = self.reddit.subreddit(subreddit).random()
            await self.redfunc(ctx, subreddit=subreddit, oldurl=post.url, stickied=post.stickied, over_18=post.over_18, title=post.title, selftext=post.selftext, origin="new")
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

    #async def red(self, ctx, *, subreddit):
#
    #    #
    #    #   Request random post json from reddit
    #    #
    #    if self.redditdebug:
    #        print("new")
    #    query = requests.get("https://oauth.reddit.com/r/" + subreddit + "/random.json", headers=self.headers)
    #    #print(query.status_code)
#
    #    #
    #    #   If query responds with 401, reauthorize client
    #    #
    #    if query.status_code == 401:
    #        await self.authorize()
    #        query = requests.get("https://oauth.reddit.com/r/" + subreddit + "/random.json", headers=self.headers)
#
    #    #
    #    #   Make sure to parse query as json, check if json is instance of list, if it is get first instance in list
    #    #
    #    postin = query.json()
    #    if isinstance(postin, list):
    #        postin = postin[0]
#
    #    #
    #    #   Parse through json to easily get variables needed from post
    #    #
    #    postjson = postin.get("data")
    #    postjson = postjson.get("children")
    #    postjson = postjson[0]
    #    post = postjson.get("data")
    #    # print(i)
#
    #    await self.redfunc(ctx, subreddit=subreddit, oldurl=post.get("url"), stickied=post.get("stickied"), over_18=post.get("over_18"), title=post.get("title"), selftext=post.get("selftext"), origin="new")


    @_reddit.command()
    async def rdebug(self, ctx):
        """Turn on debug mode for the reddit command"""
        if self.redditdebug is False:
            self.redditdebug = True
            await ctx.send("Enabled reddit debug output in console!")
        else:
            self.redditdebug = False
            await ctx.send("Disabled reddit debug output in console!")

    @_reddit.command()
    async def albumlimit(self, ctx, *, limit):
        """Set the limit on pictures from albums"""
        self.alimit = int(limit)
        await ctx.send("Set number of album pictures to post at once to: " + str(self.alimit))

    @_reddit.command()
    async def rtest(self, ctx, *, subreddit):
        """Test command"""
        await ctx.send("Nothing to test. test")

    @_reddit.command()
    async def version(self, ctx):
        await ctx.send(embed=discord.Embed(title="Reddit Cog Info").add_field(name="Version", value="1.0.0")

    @commands.command()
    async def random(self,ctx):
        """Get Random subreddit post"""
        await self.randomfunc(ctx)

    async def randomfunc(self, ctx):
        if ctx.channel.is_nsfw() == True:
            subreddit = str(self.reddit.random_subreddit(nsfw=True))
        elif ctx.channel.is_nsfw() == False:
            subreddit = str(self.reddit.random_subreddit())
        #print(subreddit)
        self.randatt = True
        await self.redditcommand(ctx, subreddit=subreddit)