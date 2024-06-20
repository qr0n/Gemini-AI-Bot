import json
from discord.ext import commands
from discord import Message
from modules.ContextWindow import ContextWindow
import random

context_window = ContextWindow.context_window

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

class Freewill(commands.Cog):
    def __init__(self, bot):
        self.bot : commands.Bot = bot
    
    @commands.Cog.listener("on_message")
    async def freewill(self, message : Message):
        if config["FREEWILL"]["enabled"]:

            channel_id = message.channel.id
            text_frequency = config["FREEWILL"]["text_frequency"]
            reaction_frequency = config["FREEWILL"]["reaction_frequency"]
            
            if channel_id not in context_window:
                context_window[message.channel.id] = []
            
            if len(context_window[channel_id]) > config["MAX_CONTEXT_WINDOW"]:
                context_window[channel_id].pop(0)

            context_window[message.channel.id].append(f"{message.author.display_name}: {message.content}")

            if random.random() < text_frequency:
                prompt_plus = "You are now engaging or adding your own thoughts to this conversation, keep your reply as short as possible but make sure it makes sense and is relevant to the current topic. You will never roleplay as someone you are not instructed to roleplay as, you will use the language last used in your context window to make a response. You must not assume the conversation relates to you."