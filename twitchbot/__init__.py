from .twitchbot import Twitchbot

def setup(bot):
    n = Twitchbot(bot)
    bot.add_cog(n)