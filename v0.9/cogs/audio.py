from discord.ext import commands
from modules.BotModel import BotModel

class Audio(commands.Cog):
    def __init__(self, bot):
        self.bot : commands.Bot = bot
    
    @commands.command()
    async def analyse(self, ctx):
        file = await BotModel.upload_attachment()
        

async def setup(bot : commands.Bot):
    await bot.add_cog(Audio(bot))