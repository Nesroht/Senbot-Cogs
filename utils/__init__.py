from .utils import Utils

def setup(bot):
    n = Utils(bot)
    bot.remove_command("ping")
    bot.add_cog(n)