import discord
import time
import aiohttp
import inspect
from redbot.core import checks, Config, commands
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.utils.chat_formatting import box
import nekos




class Neko(commands.Cog):
    """Neko commands for Senbot"""

    def __init__(self, bot):
        self.bot = bot
        self._session = aiohttp.ClientSession(loop=self.bot.loop)

    @commands.command()
    async def neko(self, ctx, *, str):
        """Reply with latency of bot"""
        try:
            emb = discord.Embed(title="Have some " + str.capitalize(), color=discord.Color.red())
            emb.set_image(url=nekos.img(str))
            await ctx.send(embed=emb)
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")