import json
import datetime
import aiohttp
import os
from discord.ext import commands
from discord import Message, Reaction, AllowedMentions
from modules.Memories import Memories
from modules.ContextWindow import ContextWindow
from modules.BotModel import read_prompt, BotModel
from PIL import Image

context_window = ContextWindow().context_window
allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False)

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

async def download_attachment(attachment):
    async with aiohttp.ClientSession() as session:
        async with session.get(attachment.url) as response:
            if response.status == 200:
                file_content = await response.read()
                # Save the file to the current directory
                with open(attachment.filename, "wb") as file:
                    file.write(file_content)
                print(f'Downloaded {attachment.filename}')
            else:
                print(f'Failed to download {attachment.filename}')

class MessagerBeta(commands.Cog, name="Gemini AI Bot - Beta"):
    # Implement reactions to reactions (discord)
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @commands.Cog.listener('on_message')
    async def ai_listen(self, message : Message):
        
        ctx = await self.bot.get_context(message)
        channel_id = ctx.channel.id
        
        with open("activation.json", "r") as ul_activated_channels:
            activated_channels: dict = json.load(ul_activated_channels)

        if message.author.id == self.bot.user.id:
            return
        
        if not self.bot.user.mentioned_in(message):
            return
        
        if channel_id not in context_window:
            context_window[channel_id] = []

        context_window[channel_id].append(f"{message.author.display_name}: {message.content}") # REIMPLEMENT THIS EVERYWHERE THIS STANDARD IS NOT BEING USED EVERYWHERE

        if len(context_window[channel_id]) > config["GEMINI"]["MAX_CONTEXT_WINDOW"]:
            context_window[channel_id].pop(0)
        
        await ctx.channel.typing()

        attachments = ctx.message.attachments

        remembered_memories = Memories().compare_memories(channel_id, ctx.message.content)
        if remembered_memories["is_similar"]:
            prompt = read_prompt(ctx.message, remembered_memories['similar_phrase'])
        else:
            prompt = read_prompt(ctx.message)

        if attachments:
            save_name = f"{message.guild.id}-{message.id}-{ctx.message.attachments[0].filename}"
            await ctx.message.attachments[0].save(save_name) # download attachments[0] 
            image = Image.open(save_name)
            await ctx.reply(BotModel.generate_content(prompt, channel_id, image), mention_author=False, allowed_mentions=allowed_mentions)
            image.close()
            os.remove(save_name) # deletes file
        else:
            await ctx.reply(BotModel.generate_content(prompt, channel_id), mention_author=False, allowed_mentions=allowed_mentions)

    @commands.Cog.listener("on_reaction_add")
    async def on_rxn_add(self, reaction : Reaction, user):
        
        if reaction.message.author.id is not self.bot.user.id: 
            return
        
        channel_id = reaction.message.channel.id
        
        if channel_id not in context_window:
            context_window[channel_id] = []
            
        context_window[channel_id].append(f"{user.name} reacted with '{reaction.emoji}' to your message '{reaction.message.content}'")

    @commands.command()
    async def wack(self, ctx):
        try:
            channel_id = ctx.channel.id
            len_delete = len(context_window[channel_id])
            del context_window[channel_id]
        except KeyError:
            await ctx.reply(config["MESSAGES"]["wack_error"] or "No context window found. :pensive:", mention_author=False)
            return
        await ctx.reply(config["MESSAGES"]["wack"] or f"Context window cleared [Removed {len_delete} memories] :ok_hand:", mention_author=False)
    
    @commands.command()
    async def dump_ctx_window(self, ctx):
        filename = str(datetime.datetime.now().timestamp()) + ".json" 
        with open(filename, "w") as new_context_window:
            new_context_window.write(str(context_window))
            new_context_window.close()
        await ctx.reply(f"Saved context window to {filename}", mention_author=False)

    @commands.command()
    async def activate(self, ctx):
        with open("activation.json", "r") as unloaded_activated_channel:
            activated_channels = json.load(unloaded_activated_channel)
            activated_channels[ctx.channel.id] = True
        with open("activation.json", "w") as unloaded_activated_channel:
            json.dump(activated_channels, unloaded_activated_channel)
            await ctx.reply("Activated.", mention_author=False)
             
async def setup(bot : commands.Bot):
	await bot.add_cog(MessagerBeta(bot))