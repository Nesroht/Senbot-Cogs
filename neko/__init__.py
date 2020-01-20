from .neko import Neko

def setup(bot):
    n = Neko(bot)
    bot.add_cog(n)