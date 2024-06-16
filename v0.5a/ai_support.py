import discord
from discord.ext import commands
import os
from modules.ContextWindow import ContextWindow

context_window = ContextWindow.context_window

class AISupport(commands.Cog, name="AI-Support"):
    
    def __init__(self, bot):
        self.bot : commands.Bot = bot
    
    @commands.command()
    async def wack(self, ctx):
        try:
            user_id = f"{(ctx.guild.id)}-{ctx.author.id}"
            len_delete = len(context_window[user_id])
            del context_window[f"{ctx.guild.id}-{ctx.author.id}"]
        except KeyError:
            return await ctx.reply("No context window found. :pensive:")
        return await ctx.reply(f"Context window cleared [Removed {len_delete} memories] :ok_hand:")
    
    @commands.command()
    async def delete(self, ctx, message : discord.Message):
        try:
            if message.author.id is not self.bot.user.id:
                await ctx.reply("Sorry, that is not my message.", mention_author=False, delete_after=2)
            else:
                await message.delete()
        except Exception as E:
            print("Error")

async def setup(bot):
	await bot.add_cog(AISupport(bot))