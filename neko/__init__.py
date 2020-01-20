from .neko import Utils

def setup(bot):
    n = Neko(bot)
    bot.add_cog(n)