from .nsfw import NSFW

def setup(bot):
    n = NSFW(bot)
    bot.add_cog(n)
    bot.loop.create_task(n.boob_knowlegde())