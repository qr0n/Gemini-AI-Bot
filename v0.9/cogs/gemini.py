from discord import Message, AllowedMentions, Reaction
from discord.ext import commands
from modules.DiscordBot import Gemini
from modules.BotModel import load_character_details
from modules.ManagedMessages import ManagedMessages
from modules.MemoriesBeta import Memories

import json

allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False)

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

class GeminiCog(commands.Cog):

    def __init__(self, bot):
        self.bot : commands.Bot = bot
    
    def is_activated(self, channel_id) -> bool:
        with open("./activation.json", "r") as ul_activation:
            activated: dict = json.load(ul_activation)
            return bool(activated.get(str(channel_id), False))
        
    @commands.Cog.listener("on_message")
    async def listen(self, message : Message):
        channel_id = message.channel.id

        if message.author.id == self.bot.user.id:
            return
        
        if self.bot.user.mentioned_in(message) or self.is_activated(channel_id):
            pass
        else:
            return

        await message.channel.typing()
        # do stuff here? 

        response = await Gemini.generate_response(message)
        
        if response == "[]":
            return await message.reply(config["MESSAGES"]["error"])
        
        
        chunks = [response[i:i + 2000] for i in range(0, len(response), 2000)]

        for chunk in chunks:
            try:
                text = await message.reply(chunk, mention_author=False, allowed_mentions=allowed_mentions)
                await ManagedMessages.add_to_message_list(channel_id=channel_id, message_id=text.id, message=f"{load_character_details()['name']}: {text.content}")
            except Exception as E:
                print(f"Error replying response: {E}")

    @commands.Cog.listener("on_reaction_add")
    async def on_rxn_add(self, reaction : Reaction, user):
        
        if reaction.message.author.id is not self.bot.user.id and not reaction.is_custom_emoji(): 
            return
        
        channel_id = reaction.message.channel.id
        
        if channel_id not in ManagedMessages.context_window:
            ManagedMessages.context_window[channel_id] = []
            
        match reaction.emoji:
            
            case "🔇":
                await ManagedMessages.remove_from_message_list(channel_id, reaction.message.id)
            
            case "⭐":
                print("User liked message")

            case _:
                await ManagedMessages.add_to_message_list(channel_id, reaction.message.id, f"{user.name} reacted with '{reaction.emoji}' to your message '{reaction.message.content}'")

    @commands.command()
    async def wack(self, ctx : Message):
        await ctx.reply(await ManagedMessages.remove_channel_from_list(ctx.channel.id))
    
    @commands.command()
    async def activate(self, ctx):
        with open("./activation.json", "r") as unloaded_activated_channel:
            activated_channels = json.load(unloaded_activated_channel)
            activated_channels[ctx.channel.id] = True

        with open("./activation.json", "w") as unloaded_activated_channel:
            json.dump(activated_channels, unloaded_activated_channel)

            activated_string = config["MESSAGES"]["activated_message"] or f"{self.bot.user.name} is activated in <#{ctx.channel.id}>"
            await ctx.reply(activated_string, mention_author=False)

    @commands.command()
    async def deactivate(self, ctx):
        with open("./activation.json", "r") as unloaded_activated_channel:
            activated_channels = json.load(unloaded_activated_channel)
            del activated_channels[str(ctx.channel.id)]

        with open("./activation.json", "w") as unloaded_activated_channel:
            json.dump(activated_channels, unloaded_activated_channel)

            activated_string = config["MESSAGES"]["deactivated_message"] or f"{self.bot.user.name} has deactivated in <#{ctx.channel.id}>"
            await ctx.reply(activated_string, mention_author=False)

    @commands.command()
    async def compare_memories(self, ctx : commands.Context):
        await ctx.reply(Memories().compare_memories(message=None), mention_author=False)

    @commands.command()
    async def force_save(self, ctx : commands.Context):
        user_id = f"{ctx.guild.id}-{ctx.author.id}"
        await Memories().save_to_memory(ctx.message, force=True)
    
    @commands.command()
    async def fetch_mem(self, ctx : commands.Context):
        user_id = f"{ctx.guild.id}-{ctx.author.id}"
        await ctx.reply(Memories().fetch_and_sort_entries(user_id), mention_author=False)
    
    @commands.command()
    async def compare_mem(self, ctx : commands.Context, *memory):
        user_id = f"{ctx.guild.id}-{ctx.author.id}"
        await ctx.reply(await Memories().compare_memories(user_id, message=memory), mention_author=False)
        

async def setup(bot: commands.Bot):
    await bot.add_cog(GeminiCog(bot))