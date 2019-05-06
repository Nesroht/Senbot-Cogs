from .reddit import Reddit

def setup(bot):
    n = Reddit(bot)
    bot.add_cog(n)