from redbot.core import commands

class NSFW(commands.Cog):
    """My custom cog"""

    @commands.command()
    async def dicks(self, ctx):
        """This does stuff!"""
        # Your code will go here
        await ctx.send("I can do stuff! NSFW!")