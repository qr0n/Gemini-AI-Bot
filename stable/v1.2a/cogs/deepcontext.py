from discord.ext import commands
from modules.DeepContext import DeepContext


class deepcontext(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.command()
    async def test_dc(self, ctx: commands.Context, *, text):
        classification = await DeepContext.Logic.classify(text, ctx.author.name)
        await ctx.send(classification)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(deepcontext(bot))
