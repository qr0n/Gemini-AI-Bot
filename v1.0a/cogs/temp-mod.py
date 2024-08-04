import discord
from discord.ext import commands
from discord import Message

db = {}

class ModerationCommands(commands.Cog, name='Moderation Commands'):
    '''These are the commands used by Moderation'''
    
    def __init__(self, bot):
        self.bot = bot
        print("Moderation Cog Loaded")  
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def shh(self, ctx, mutee : discord.Member):
        db[str(mutee.id)] = True
        await ctx.reply(f"`{mutee.id}` has been shh'd.", mention_author=False)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unshh(self, ctx, mutee : discord.Member):
        db[str(mutee.id)] = False
        await ctx.reply(f"`{mutee.id}` has been unshh'd.", mention_author=False)

    @commands.command()
    async def clean(self, ctx, limit=5):
        await ctx.channel.purge(limit=limit)

    @commands.Cog.listener('on_message')
    async def listen_for_shh(self, msg):
        try:
            if db[str(msg.author.id)]:
                await msg.delete()
        except KeyError:
            return None

async def setup(bot):
    await bot.add_cog(ModerationCommands(bot))