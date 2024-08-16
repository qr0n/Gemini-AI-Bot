import json
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
from modules.AIAgent import AIAgent

class discord_AIAgent(commands.Cog, name='AIAgent'):
    '''These commands are used to control the AI'''

    def __init__(self, bot):
        self.bot : commands.Bot = bot

    @commands.command()
    async def categorize(self, ctx : Context, *, data):
        """Clears the bot's context window, resetting the conversation"""
        await ctx.send(await AIAgent.classify(data))

    @commands.Cog.listener('on_message')
    async def classify(self, message : discord.Message):
        if message.author.id == 578789460141932555:
        
            category = await AIAgent.classify(message.content)
            await message.reply(category)
            await AIAgent.categorize(category, await self.bot.get_context(message))
        
        else:
            return
        
    @tasks.loop(seconds=5)
    async def get_and_sort_reminders(self)

def setup(bot : commands.Bot):
    bot.add_cog(discord_AIAgent(bot))
    