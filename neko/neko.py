import discord
import time
import aiohttp
import inspect
from redbot.core import checks, Config, commands
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.utils.chat_formatting import box
from .constants import NSFW, SFW, RANDOM
import nekos




class Neko(commands.Cog):
    """Neko commands for Senbot"""


    def __init__(self, bot):
        self.bot = bot
        self._session = aiohttp.ClientSession(loop=self.bot.loop)


    @commands.command()
    async def neko(self, ctx, *, str):
        """Ask the Neko api for picture"""
        try:
            if ctx.guild:
                if ctx.channel.is_nsfw() == True:
                    if str in NSFW or str in SFW or str in RANDOM:
                        emb = discord.Embed(title="Random " + str.capitalize(), color=discord.Color.red())
                        emb.set_image(url=nekos.img(str))
                        await ctx.send(embed=emb)
                    else:
                        await self.noOptionMsg(ctx,str)
                else:
                    if str in SFW or str in RANDOM:
                        emb = discord.Embed(title="Random " + str, color=discord.Color.red())
                        emb.set_image(url=nekos.img(str))
                        await ctx.send(embed=emb)
                    elif str in (NSFW):
                        await ctx.send(box("Only allowed in NSFW channels or DM's"))
                    else:
                        await self.noOptionMsg(ctx, str)
            else:
                if str in NSFW or str in SFW or str in RANDOM:
                    emb = discord.Embed(title="Random " + str.capitalize(), color=discord.Color.red())
                    emb.set_image(url=nekos.img(str))
                    await ctx.send(embed=emb)
                else:
                    await self.noOptionMsg(ctx,str)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")


    @commands.command()
    async def slap(self, ctx, user : discord.Member):
        if ctx.guild:
            emb = discord.Embed(title=ctx.author.display_name + " slaps " + user.display_name, color=discord.Color.blurple())
            emb.set_image(url=nekos.img('slap'))
            await ctx.send(embed=emb)

    @commands.command()
    async def hug(self, ctx, user: discord.Member):
        if ctx.guild:
            emb = discord.Embed(title=ctx.author.display_name + " hugs " + user.display_name,
                                color=discord.Color.blurple())
            emb.set_image(url=nekos.img('hug'))
            await ctx.send(embed=emb)

    @commands.command()
    async def cuddle(self, ctx, user: discord.Member):
        if ctx.guild:
            emb = discord.Embed(title=ctx.author.display_name + " cuddles with " + user.display_name,
                                color=discord.Color.blurple())
            emb.set_image(url=nekos.img('cuddle'))
            await ctx.send(embed=emb)

    @commands.command()
    async def kiss(self, ctx, user: discord.Member):
        if ctx.guild:
            emb = discord.Embed(title=ctx.author.display_name + " kisses " + user.display_name,
                                color=discord.Color.blurple())
            emb.set_image(url=nekos.img('kiss'))
            await ctx.send(embed=emb)

    @commands.command()
    async def pat(self, ctx, user: discord.Member):
        if ctx.guild:
            emb = discord.Embed(title=ctx.author.display_name + " pats " + user.display_name,
                                color=discord.Color.blurple())
            emb.set_image(url=nekos.img('pat'))
            await ctx.send(embed=emb)

    @commands.command()
    async def coffee(self, ctx, user: discord.Member):
        if ctx.guild:
            emb = discord.Embed(title=ctx.author.display_name + " hands " + user.display_name + " some coffee.",
                                color=discord.Color.blurple())
            emb.set_image(url=self.nekobot("coffee"))
            await ctx.send(embed=emb)

    async def nekobot(self, imgtype: str):
        async with self.session.get("https://nekobot.xyz/api/image?type=%s" % imgtype) as res:
            res = await res.json()
        return res.get("message")


    async def noOptionMsg(self,ctx, str):
        emb = discord.Embed(title=str + " is not available", color=discord.Color.red())
        emb.add_field(name="NSFW", value=", ".join(NSFW))
        emb.add_field(name="SFW", value=", ".join(SFW))
        emb.add_field(name="RANDOM", value=", ".join(RANDOM))
        await ctx.send(embed=emb)