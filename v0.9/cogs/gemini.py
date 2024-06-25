import json
import datetime
import os
import asyncio
import google.generativeai as genai
from discord.ext import commands
from discord import Message, Reaction, AllowedMentions
from modules.Memories import Memories
from modules.ContextWindow import ContextWindow
from modules.BotModel import read_prompt, BotModel

context_window = ContextWindow().context_window
allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False)

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

genai.configure(api_key=config["GEMINI"]["API_KEY"])

async def upload_attachment(attachment : genai.types.File):
    genai_attach = genai.upload_file(attachment)
    while genai_attach.state.name == "PROCESSING":
        print("processing")
        await asyncio.sleep(0.5)
    return genai.get_file(attachment.name)
    
class Messager(commands.Cog, name="Gemini AI Bot - Beta"):
    # Implement reactions to reactions (discord)
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @commands.Cog.listener('on_message')
    async def ai_listen(self, message : Message):
        
        ctx = await self.bot.get_context(message)
        channel_id = ctx.channel.id
        
        with open("./activation.json", "r") as ul_activated_channels:
            activated_channels = json.load(ul_activated_channels)

        if message.author.id == self.bot.user.id:
            return
        
        if not self.bot.user.mentioned_in(message) or not activated_channels[str(ctx.channel.id)]:
            return
        
        if channel_id not in context_window:
            context_window[channel_id] = []

        context_window[channel_id].append(f"{message.author.display_name}: {message.content}") # REIMPLEMENT THIS EVERYWHERE THIS STANDARD IS NOT BEING USED EVERYWHERE

        if len(context_window[channel_id]) > config["GEMINI"]["MAX_CONTEXT_WINDOW"]:
            context_window[channel_id].pop(0)
        
        await ctx.channel.typing()

        attachments = ctx.message.attachments

        remembered_memories = await Memories().compare_memories(channel_id, ctx.message.content)
        if remembered_memories["is_similar"]:
            prompt = read_prompt(ctx.message, remembered_memories['similar_phrase'])
        else:
            prompt = read_prompt(ctx.message)

        if attachments and attachments[0].filename.endswith((".png", ".jpg", ".webp", ".heic", ".heif", ".mp4", ".mpeg", ".mov", ".wmv",)):
            save_name = ctx.message.attachments[0].filename.lower()
            await ctx.message.attachments[0].save(save_name) # download attachments[0]
            
            file = await upload_attachment(save_name)

            await ctx.reply(await BotModel.generate_content(prompt, channel_id, file), mention_author=False, allowed_mentions=allowed_mentions) # Send off file name to GenAI.upload_file 
            # TODO Update in freewill
            print(save_name)
            # genai.delete_file(save_name) # deletes file on Google
            
            os.remove(save_name) # deletes file locally 
        else:
            await ctx.reply(await BotModel.generate_content(prompt, channel_id), mention_author=False, allowed_mentions=allowed_mentions)

    @commands.Cog.listener("on_reaction_add")
    async def on_rxn_add(self, reaction : Reaction, user):
        
        if reaction.message.author.id is not self.bot.user.id: 
            return
        
        channel_id = reaction.message.channel.id
        
        if channel_id not in context_window:
            context_window[channel_id] = []
            
        if reaction.emoji != "♻":
            context_window[channel_id].append(f"{user.name} reacted with '{reaction.emoji}' to your message '{reaction.message.content}'")
        else:
            pass # do regeneration logic, pop last message in context window, get last message sent in channel, regenerate response

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
        filename = str(datetime.datetime.now().timestamp()) + ".txt" 
        with open(filename, "w", encoding="utf-8") as new_context_window:
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
	await bot.add_cog(Messager(bot))