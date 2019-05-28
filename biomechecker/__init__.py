from .biomechecker import Biomechecker

def setup(bot):
    n = biomechecker(bot)
    bot.add_cog(n)