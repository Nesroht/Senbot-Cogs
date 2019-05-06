import discord
import time
import aiohttp
from redbot.core import checks, Config, commands



class Utils(commands.Cog):
    """Utility commands for Senbot"""

    def __init__(self, bot):
        self.bot = bot
        self._session = aiohttp.ClientSession(loop=self.bot.loop)

    @commands.command()
    async def ping(self, ctx,):
        """Reply with latency of bot"""
        latency = self.bot.latency * 1000
        emb = discord.Embed(title="Pong!", color=discord.Color.red())
        emb.add_field(name="Discord", value="```" + str(round(latency)) + " ms```")
        emb.add_field(name="Typing", value="```" + "calculating" + " ms```")

        before = time.monotonic()
        message = await ctx.send(embed=emb)
        ping = (time.monotonic() - before) * 1000

        emb = discord.Embed(title="Pong!", color=discord.Color.green())
        emb.add_field(name="Discord", value="```" + str(round(latency)) + " ms```")
        emb.add_field(name="Typing", value="```" + str(round(ping)) + " ms```")

        await message.edit(embed=emb)

