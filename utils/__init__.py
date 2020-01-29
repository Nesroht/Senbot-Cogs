from .utils import Utils

def setup(bot):
    n = Utils(bot)
    bot.add_cog(n)