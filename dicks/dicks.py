from redbot.core import commands

class Dicks(commands.Cog):
    """My custom cog"""

    @commands.command()
    async def dicks(self, ctx):
        """This does stuff!"""
        # Your code will go here
        await ctx.send("I can do stuff! dicks!")