import discord
import time
import aiohttp
import inspect
from redbot.core import checks, Config, commands
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.utils.chat_formatting import box



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
        emb.add_field(name="Discord", value=box(str(round(latency)) + " ms"))
        emb.add_field(name="Typing", value=box("calculating" + " ms"))

        before = time.monotonic()
        message = await ctx.send(embed=emb)
        ping = (time.monotonic() - before) * 1000

        emb = discord.Embed(title="Pong!", color=discord.Color.green())
        emb.add_field(name="Discord", value=box(str(round(latency)) + " ms"))
        emb.add_field(name="Typing", value=box(str(round(ping)) + " ms"))

        await message.edit(embed=emb)

    @commands.command()
    async def botstats(self,ctx):
        """Reply with stats of bot"""
        users = str(len(self.bot.users))
        servers = str(len(self.bot.guilds))
        emb = discord.Embed(title="Stats", description="Various stats regarding the bot", color=discord.Color.blurple())
        emb.add_field(name="Users", value=box(users))
        emb.add_field(name="Servers", value=box(servers))
        await ctx.send(embed=emb)

    @commands.command()
    @checks.is_owner()
    async def sourcecode(self, ctx, *, command: str):
        """
        Get the source code of a command
        """
        command = self.bot.get_command(command)
        if command is None:
            await ctx.send("Command not found.")
            return
        source_code = inspect.getsource(command.callback)
        temp_pages = []
        pages = []
        for page in pagify(source_code, escape_mass_mentions=True, page_length=1980):
            temp_pages.append("```py\n" + str(page).replace("```", "``") + "```")
        max_i = len(temp_pages)
        i = 1
        for page in temp_pages:
            pages.append(f"Page {i}/{max_i}\n" + page)
            i += 1
        await menu(ctx, pages, controls=DEFAULT_CONTROLS)
