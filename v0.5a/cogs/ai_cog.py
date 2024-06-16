import json
import datetime
from discord.ext import commands
from discord import Message
from modules.Memories import Memories
from modules.ContextWindow import ContextWindow
from modules.BotModel import BotModel, read_prompt
from PIL import Image

context_window = ContextWindow().context_window

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

class Messager(commands.Cog, name="Gemini AI Bot"):
    
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener('on_message')
    async def message_generator(self, msg : Message):
        ctx = await self.bot.get_context(msg)
        
        if ctx.author.id == self.bot.user.id:
            return
        
        if not self.bot.user.mentioned_in(msg):
            return
        
        user_id = f"{ctx.guild.id}-{ctx.author.id}"

        if user_id not in context_window:
            context_window[user_id] = []
        
        context_window[user_id].append(f"{msg.author.name}: {msg.content}")

        if len(context_window[user_id]) > config["MAX_CONTEXT_WINDOW"]:
            context_window[user_id].pop(0)
        
        await ctx.channel.typing()

        remembered_memories = Memories().compare_memories(user_id, msg.content)
        if remembered_memories['is_similar']:
            prompt = read_prompt(msg, remembered_memories['similar_phrase'])
        else:
            prompt = read_prompt(msg)
        response = BotModel.generate_content(prompt, user_id=user_id)
        Memories().save_to_memory(msg)

        character_name = Memories.load_character_details()["name"]
        if response.startswith(f"{character_name}: "):
                response = response[len(f"{character_name}: "):]

        chunks = [response[i:i + 2000] for i in range(0, len(response), 2000)]

        for chunk in chunks:
            try:
                await ctx.reply(chunk, mention_author=False)
            except Exception as E:
                print(f"Error replying response: {E}")

    @commands.Cog.listener('on_message')
    async def ai_listen(self, message : Message):
        ctx = await self.bot.get_context(message)
        if ctx.message.attachments[0].save():
            attachment = Image.open()

    @commands.command()
    async def wack(self, ctx):
        try:
            user_id = f"{(ctx.guild.id)}-{ctx.author.id}"
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
	await bot.add_cog(Messager(bot))