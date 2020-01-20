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
                    if str in (NSFW or SFW or RANDOM):
                        emb = discord.Embed(title="Have some " + str.capitalize(), color=discord.Color.red())
                        emb.set_image(url=nekos.img(str))
                        await ctx.send(embed=emb)
                    else:
                        emb2 = discord.Embed(title=str + "is not available", color=discord.Color.red())
                        emb2.add_field(name="NSFW", value=", ".join(NSFW))
                        emb2.add_field(name="SFW", value=", ".join(SFW))
                        emb2.add_field(name="RANDOM", value=", ".join(RANDOM))
                        await ctx.send(embed=emb2)
                else:
                    if str in (SFW or RANDOM):
                        emb = discord.Embed(title="Have some " + str, color=discord.Color.red())
                        emb.set_image(url=nekos.img(str))
                        await ctx.send(embed=emb)
                    #elif str in (NSFW):
                        #await ctx.send(box("Only allowed in NSFW channels or DM's"))
                    else:
                        emb2 = discord.Embed(title=str + "is not available", color=discord.Color.red())
                        emb2.add_field(name="NSFW", value=", ".join(NSFW))
                        emb2.add_field(name="SFW", value=", ".join(SFW))
                        emb2.add_field(name="RANDOM", value=", ".join(RANDOM))
                        await ctx.send(embed=emb2)
            else:
                if str in (NSFW or SFW or RANDOM):
                    emb = discord.Embed(title="Have some " + str.capitalize(), color=discord.Color.red())
                    emb.set_image(url=nekos.img(str))
                    await ctx.send(embed=emb)
                else:
                    emb2 = discord.Embed(title=str + "is not available", color=discord.Color.red())
                    emb2.add_field(name="NSFW", value=", ".join(NSFW))
                    emb2.add_field(name="SFW", value=", ".join(SFW))
                    emb2.add_field(name="RANDOM", value=", ".join(RANDOM))
                    await ctx.send(embed=emb2)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")