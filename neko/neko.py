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


    async def noOptionMsg(self,ctx):
        emb = discord.Embed(title=str + "is not available", color=discord.Color.red())
        emb.add_field(name="NSFW", value=", ".join(NSFW))
        emb.add_field(name="SFW", value=", ".join(SFW))
        emb.add_field(name="RANDOM", value=", ".join(RANDOM))
        await ctx.send(embed=emb)

    @commands.command()
    async def neko(self, ctx, *, str):
        """Ask the Neko api for picture"""
        try:
            if ctx.guild:
                if ctx.channel.is_nsfw() == True:
                    if str in NSFW or str in SFW or str in RANDOM:
                        emb = discord.Embed(title="Have some " + str.capitalize(), color=discord.Color.red())
                        emb.set_image(url=nekos.img(str))
                        await ctx.send(embed=emb)
                    else:
                        await noOptionMsg(ctx)
                else:
                    if str in SFW or str in RANDOM:
                        emb = discord.Embed(title="Have some " + str, color=discord.Color.red())
                        emb.set_image(url=nekos.img(str))
                        await ctx.send(embed=emb)
                    elif str in (NSFW):
                        await ctx.send(box("Only allowed in NSFW channels or DM's"))
                    else:
                        await noOptionMsg(ctx)
            else:
                if str in NSFW or str in SFW or str in RANDOM:
                    emb = discord.Embed(title="Have some " + str.capitalize(), color=discord.Color.red())
                    emb.set_image(url=nekos.img(str))
                    await ctx.send(embed=emb)
                else:
                    await noOptionMsg(ctx)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")


    @commands.command()
    async def slap(self, ctx, user):
        try:
            if ctx.guild:
                emb = discord.Embed(title=ctx.author.nick + " slaps " + user.mention, color=discord.Color.blurple())
                emb.set_image(url=nekos.img('slap'))
                await ctx.send(embed=emb)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")