import json
import datetime
import aiohttp
from discord.ext import commands
from discord import Message, Reaction, User
from modules.MemoriesBeta import Memories
from modules.ContextWindow import ContextWindow
from modules.BotModel import read_prompt, BotModel

context_window = ContextWindow().context_window

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

class Gemini(commands.Cog, name="Gemini AI Bot - Beta"):
    # This is a cog, or an extension

    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @commands.Cog.listener('on_message')
    async def ai_listen(self, message : Message):
        # This is an on_message event handler,
        # meaning, the code below gets executed everytime a message is sent
        # to a channel the bot can access
        
        ctx : commands.Context = await self.bot.get_context(message) # this is just... neatening? ctx is basically just Message
        user_id = f"{ctx.guild.id}-{ctx.author.id}" # uuid (unique user identification)
        
        with open("activation.json", "r") as ul_activated_channels:
            activated_channels: dict = json.load(ul_activated_channels)

        if message.author.id == self.bot.user.id:
            return
        
        if not self.bot.user.mentioned_in(message):
            return
        
        if user_id not in context_window:
            context_window[user_id] = []

        # Three (3) checks occur
        
        # Check 1 (anti self-reply)
        # This checks if the message author id is the bot, if it is the function terminates

        # Check 2 (only on mention)
        # This check is making sure that the bot is mentioned in the message, 
        # this includes replies even with the @ off

        # Check 3 (user id in context window)
        # This check makes sure that the bot doesnt 

        context_window[user_id].append(f"{message.author.name}: {message.content}\n")
        # This appends the message author name, along with the content
        # Example
        # iron : hello!\n
        # \n is a new line character, it forces creation of a new line

        if len(context_window[user_id]) > config["GEMINI"]["MAX_CONTEXT_WINDOW"]:
            context_window[user_id].pop(0)

        # This checks if the context window exceeds a certain number in config.json
        # if it is, it removes the first item
        # Example
        # _list = ["hello", "world", "i", "am", "a", "list"]
        # _list.pop(0)
        # >>> ["world", "i", "am", "a", "list"]
        
        await ctx.channel.typing()

        # This makes the bot type for 2 seconds

        remembered_memories = Memories().compare_memories(user_id, ctx.message.content)
        if remembered_memories["is_similar"]:
            prompt = read_prompt(ctx.message, remembered_memories['similar_phrase'])
        else:
            prompt = read_prompt(ctx.message)

        # LTM support
        # first check, L75
        # This check is done to make sure that the bot recognizes something
        # As being similar in its LTM DB
        # if it is, the dictionary Gemini creates should look like this
        # {"is_similar" : True, "similar_phrase" : phrase}

        # This then appended to the 'read_prompt' function
        # if there is an LTM, what happens is the memory gets indexed and sent off to gemini

        response = BotModel.generate_content(prompt, user_id)
        context_window[user_id].append(response)

        chunks = [response[i:i + 2000] for i in range(0, len(response), 2000)]

        for chunk in chunks:
            try:
                await message.reply(chunk, mention_author=False, allowed_mentions=None)
            except Exception as E:
                print(f"Error replying response: {E}")
        
        # New for 0.8-alpha-json 

        # Message Chunking
        # This code firstly appends the entire response to the context window
        # then it loops through the chunk list checking to see if the response is greater than 2000
        # then it truncates it and sends the first chunk, after it sends the other chunk

    @commands.Cog.listener("on_reaction_add")
    async def on_rxn_add(self, reaction : Reaction, user):

        # This is the on_reaction_add event listener
        
        if reaction.message.author.id is not self.bot.user.id: 
            return
        
        user_id = f"{reaction.message.guild.id}-{user.id}"
        
        if user_id not in context_window:
            context_window[user_id] = []
            
        # same stuff you know.. uuid, check 1 check 2

        context_window[user_id].append(f"{user.name} reacted with '{reaction.emoji}' to your message '{reaction.message.content}'")
        # appends the reaction to the context window

    @commands.command()
    async def wack(self, ctx : commands.Context):
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
    async def compare_memories(self, ctx):
        await ctx.reply(Memories().compare_memories(message=None), mention_author=False)

    @commands.command()
    async def force_save(self, ctx):
        user_id = f"{ctx.guild.id}-{ctx.author.id}"
        Memories().save_to_memory(ctx.message, force=True)
    
    @commands.command()
    async def fetch_mem(self, ctx):
        user_id = f"{ctx.guild.id}-{ctx.author.id}"
        await ctx.reply(Memories().fetch_and_sort_entries(user_id), mention_author=False)
    
    @commands.command()
    async def compare_mem(self, ctx, *memory):
        user_id = f"{ctx.guild.id}-{ctx.author.id}"
        await ctx.reply(Memories().compare_memories(user_id, message=memory), mention_author=False)
                 
async def setup(bot : commands.Bot):
	await bot.add_cog(Gemini(bot))