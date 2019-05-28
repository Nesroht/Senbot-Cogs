from .biomechecker import biomechecker

def setup(bot):
    n = biomechecker(bot)
    bot.add_cog(n)