import json
import datetime
import aiohttp
from discord.ext import commands
from discord import Message, Reaction, User
from modules.Memories import Memories
from modules.ContextWindow import ContextWindow
from modules.BotModel import read_prompt, BotModel
from PIL import Image

context_window = ContextWindow().context_window

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
        user_id = f"{ctx.guild.id}-{ctx.author.id}"
        
        with open("activation.json", "r") as ul_activated_channels:
            activated_channels: dict = json.load(ul_activated_channels)

        if message.author.id == self.bot.user.id:
            return
        
        if not self.bot.user.mentioned_in(message):
            return
        
        if user_id not in context_window:
            context_window[user_id] = []

        context_window[user_id].append(f"{message.author.name}: {message.content}")

        if len(context_window[user_id]) > config["MAX_CONTEXT_WINDOW"]:
            context_window[user_id].pop(0)
        
        await ctx.channel.typing()

        attachments = ctx.message.attachments

        remembered_memories = Memories().compare_memories(user_id, ctx.message.content)
        if remembered_memories["is_similar"]:
            prompt = read_prompt(ctx.message, remembered_memories['similar_phrase'])
        else:
            prompt = read_prompt(ctx.message)

        if attachments:
            save_name = f"{message.guild.id}-{message.id}-{ctx.message.attachments[0].filename}"
            await ctx.message.attachments[0].save(save_name)
            image = Image.open(save_name)
            await ctx.reply(BotModel.generate_content(prompt, user_id, image), mention_author=False)
            image.close() # download attachments[0] in `attachments` 
        else:
            await ctx.reply(BotModel.generate_content(prompt, user_id), mention_author=False)

    @commands.Cog.listener("on_reaction_add")
    async def on_rxn_add(self, reaction : Reaction, user):
        
        if reaction.message.author.id is not self.bot.user.id: 
            return
        
        user_id = f"{reaction.message.guild.id}-{user.id}"
        
        if user_id not in context_window:
            context_window[user_id] = []
            
        context_window[user_id].append(f"{user.name} reacted with '{reaction.emoji}' to your message '{reaction.message.content}'")

    @commands.command()
    async def wack(self, ctx : Message):
        try:
            user_id = f"{ctx.guild.id}-{ctx.author.id}"
            len_delete = len(context_window[user_id])
            del context_window[f"{ctx.guild.id}-{ctx.author.id}"]
        except KeyError:
            await ctx.reply("No context window found. :pensive:", mention_author=False)
            return
        await ctx.reply(f"Context window cleared [Removed {len_delete} memories] :ok_hand:", mention_author=False)
    
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
