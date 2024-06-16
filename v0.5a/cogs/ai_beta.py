import json
import datetime
from discord.ext import commands
from discord import Message
from modules.Memories import Memories
from modules.ContextWindow import ContextWindow
from PIL import Image

context_window = ContextWindow().context_window

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

class MessagerBeta(commands.Cog, name="Gemini AI Bot - Beta"):
    
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener('on_message')
    async def ai_listen(self, message : Message):
        ctx = await self.bot.get_context(message)
        attachments = ctx.message.attachments
        if attachments:
            attachments[0].save()
             

    # @commands.command()
    # async def wack(self, ctx : Message):
    #     try:
    #         user_id = f"{(ctx.guild.id)}-{ctx.author.id}"
    #         len_delete = len(context_window[user_id])
    #         del context_window[f"{ctx.guild.id}-{ctx.author.id}"]
    #     except KeyError:
    #         await ctx.reply("No context window found. :pensive:", mention_author=False)
    #         return
    #     await ctx.reply(f"Context window cleared [Removed {len_delete} memories] :ok_hand:", mention_author=False)
    
    # @commands.command()
    # async def dump_ctx_window(self, ctx):
    #     filename = str(datetime.datetime.now().timestamp()) + ".json" 
    #     with open(filename, "w") as new_context_window:
    #         new_context_window.write(str(context_window))
    #         new_context_window.close()
    #     await ctx.reply(f"Saved context window to {filename}", mention_author=False)

    # @commands.command()
    # async def activate(self, ctx):
    #     with open("activation.json", "r") as unloaded_activated_channel:
    #         activated_channels = json.load(unloaded_activated_channel)
    #         activated_channels[ctx.channel.id] = True
    #     with open("activation.json", "w") as unloaded_activated_channel:
    #         json.dump(activated_channels, unloaded_activated_channel)
    #         await ctx.reply("Activated.", mention_author=False)
            
async def setup(bot : commands.Bot):
	await bot.add_cog(MessagerBeta(bot))