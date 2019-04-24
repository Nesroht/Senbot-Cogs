
from bs4 import BeautifulSoup

import discord
from redbot.core import checks, Config, commands
# Sys
import asyncio

from urllib.request import urlopen
import requests
import requests.auth



class Nsfw(commands.Cog):
    """Nsfw cog for Senbot"""

    def __init__(self, bot):
        self.bot = bot
        self._session = aiohttp.ClientSession(loop=self.bot.loop)

    @commands.command()
    @commands.is_nsfw()
    async def yandere(self, ctx):
        """Random Image From Yandere"""
        try:
            query = ("https://yande.re/post/random")
            page = await (await self._session.get(query)).text()
            soup = BeautifulSoup(page, "html.parser")
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
            soup = BeautifulSoup(page, "html.parser")
            image = soup.find(id="highres").get("href")
            emb = discord.Embed(title="Konachan")
            emb.set_image(url=image)
            await ctx.send(embed=emb)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @commands.command()
    @commands.is_nsfw()
    async def e621(self, ctx):
        """Random Image From e621"""
        try:
            query = ("https://e621.net/post/random")
            page = await (await self._session.get(query, headers={"User-Agent":"Senbot discord bot(by Senbot on e621)"})).text()
            #await ctx.send("```"+page+"```")
            soup = BeautifulSoup(page, "html.parser")
            image = soup.find(id="highres").get("href")
            emb = discord.Embed(title="e621")
            emb.set_image(url=image)
            await ctx.send(embed=emb)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @commands.command()
    @commands.is_nsfw()
    async def rule34(self, ctx):
        """Random Image From rule34"""
        try:
            random_number = random.randint(0,100)
            if random_number < 50:
                query = ("http://rule34.xxx/index.php?page=post&s=random")
                page = await (await self._session.get(query)).text()
                soup = BeautifulSoup(page, "html.parser")
                image = soup.find(id="").get("src")
                emb = discord.Embed(title="Rule34")
                emb.set_image(url=image)
                await ctx.send(embed=emb)
            else:
                await self.newred(ctx,subreddit="rule34")

        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")

    @commands.command()
    @commands.is_nsfw()
    async def danbooru(self, ctx):
        """Random Image From Danbooru"""
        try:
            query = ("http://danbooru.donmai.us/posts/random")
            page = await (await self._session.get(query)).text()
            soup = BeautifulSoup(page, "html.parser")
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
            soup = BeautifulSoup(page, "html.parser")
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
            soup = BeautifulSoup(page, "html.parser")
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
            soup = BeautifulSoup(page, "html.parser")
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
            soup = BeautifulSoup(page, "html.parser")
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
            soup = BeautifulSoup(page, "html.parser")
            image = soup.find(id="image").get("src")
            emb = discord.Embed(title="DrunkenPumken")
            emb.set_image(url=image)
            await ctx.send(embed=emb)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")