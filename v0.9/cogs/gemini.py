from discord import Message, AllowedMentions, Reaction
from discord.ext import commands
from modules.DiscordBot import Gemini
from modules.BotModel import load_character_details
from modules.ManagedMessages import ManagedMessages
import json

allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False)

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

class TestAI(commands.Cog):

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

        await message.channel.typing()
        # do stuff here? 

        response = await Gemini.generate_response(message)

        response = await message.reply(response, allowed_mentions=allowed_mentions, mention_author=False)
        await ManagedMessages.add_to_message_list(channel_id=channel_id, message_id=response.id, message=f"{load_character_details()['name']}: {response.content}")

    @commands.Cog.listener("on_reaction_add")
    async def on_rxn_add(self, reaction : Reaction, user):
        
        if reaction.message.author.id is not self.bot.user.id: 
            return
        
        channel_id = reaction.message.channel.id
        
        if channel_id not in ManagedMessages.context_window:
            ManagedMessages.context_window[channel_id] = []
            
        if reaction.emoji != "♻":
            ManagedMessages.add_to_message_list(channel_id, reaction.message.id, f"{user.name} reacted with '{reaction.emoji}' to your message '{reaction.message.content}'")
        else:
            pass # do regeneration logic, pop last message in context window, get last message sent in channel, regenerate response


    @commands.command()
    async def wack(self, ctx : Message):
        await ctx.reply(ManagedMessages.remove_channel_from_list(ctx.channel.id))
    
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

async def setup(bot: commands.Bot):
    await bot.add_cog(TestAI(bot))