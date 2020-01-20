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
    NSFW = ['feet', 'yuri', 'trap', 'futanari', 'hololewd', 'lewdkemo', 'solog', 'feetg', 'cum', 'erokemo', 'les', 'wallpaper', 'lewdk', 'lewd', 'gecg', 'eroyuri', 'eron', 'cum_jpg', 'bj', 'nsfw_neko_gif', 'solo', 'nsfw_avatar', 'gasm', 'anal', 'hentai', 'erofeet', 'keta', 'blowjob', 'pussy', 'tits', 'holoero', 'pussy_jpg', 'pwankg', 'classic', 'kuni', 'femdom', 'spank', 'erok', 'fox_girl', 'boobs', 'random_hentai_gif', 'smallboobs', 'ero']
    SFW = ['tickle','poke','kiss','slap','cuddle','hug','pat','smug','feed','ngif','kemonomimi','neko']
    RANDOM = ['lizard','avatar','holo','waifu','8ball','goose']

    def __init__(self, bot):
        self.bot = bot
        self._session = aiohttp.ClientSession(loop=self.bot.loop)

    @commands.command()
    async def neko(self, ctx, *, str):
        """Ask the Neko api for picture"""
        try:
            if ctx.guild:
                if ctx.channel.isnsfw() == True:
                    if str in (NSFW or SFW or RANDOM):
                        emb = discord.Embed(title="Have some " + str.capitalize(), color=discord.Color.pink())
                        emb.set_image(url=nekos.img(str))
                        await ctx.send(embed=emb)
                    else:
                        await ctx.send(ctx.box("Nope"))
                else:
                    if str in (SFW or RANDOM):
                        emb = discord.Embed(title="Have some " + str, color=discord.Color.pink())
                        emb.set_image(url=nekos.img(str))
                        await ctx.send(embed=emb)
                    else:
                        await ctx.send(ctx.box("Nope"))
            else:
                if str in (NSFW or SFW or RANDOM):
                    emb = discord.Embed(title="Have some " + str.capitalize(), color=discord.Color.pink())
                    emb.set_image(url=nekos.img(str))
                    await ctx.send(embed=emb)
                else:
                    await ctx.send(ctx.box("Nope"))
        except Exception as e:
            await ctx.send(f":x: **Error:** `{e}`")