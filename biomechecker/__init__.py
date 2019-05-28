from .biomechecker import Biomechecker

def setup(bot):
    n = Biomechecker(bot)
    bot.add_cog(n)