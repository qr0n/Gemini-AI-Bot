from discord import Message, AllowedMentions, Reaction
from discord.ext import commands
from modules.DiscordBot import Gemini
from modules.BotModel import load_character_details
from modules.ManagedMessages import ManagedMessages
import json
import random
import asyncio

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False)

class NewFreewill(commands.Cog):
    
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot

    @commands.Cog.listener("on_message")
    async def freewill(self, message : Message) -> None:
        if config["FREEWILL"]["enabled"]:
            
            if message.author.id == self.bot.user.id:
                return
            
            if self.bot.user.mentioned_in(message):
                return
            
            text_frequency = config["FREEWILL"]["text_frequency"]
            reaction_frequency = config["FREEWILL"]["reaction_frequency"]
            keywords = config["FREEWILL"]["keywords"] or None
            keyword_added_chance = 0
            ctx = await self.bot.get_context(message)

            for i in keywords:
                if i.lower() in message.content.lower():
                    keyword_added_chance = config["FREEWILL"]["keywords_added_chance"]
            
            if random.random() < min(text_frequency + keyword_added_chance, 1.0):
                response = await Gemini.generate_response(message)
                
                await ctx.channel.typing()
                await asyncio.sleep(2) # artificial delay lol

                await ctx.reply(response, mention_author=False, allowed_mentions=allowed_mentions)
            
            if random.random() < min(reaction_frequency + keyword_added_chance, 1.0):
                response = await Gemini.generate_response(message)
                
                await ctx.channel.typing()
                await asyncio.sleep(2) # artificial delay lol

                await ctx.reply(response, mention_author=False, allowed_mentions=allowed_mentions)


async def setup(bot : commands.Bot):
    await bot.add_cog(NewFreewill(bot))