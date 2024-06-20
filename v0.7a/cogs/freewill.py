import json
from discord.ext import commands
from discord import Message
from modules.ContextWindow import ContextWindow

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

            if channel_id not in context_window:
                context_window[message.channel.id] = []

            
            if len(context_window[channel_id]) > config["MAX_CONTEXT_WINDOW"]:
                context_window[channel_id].pop(0)

            context_window[message.channel.id].append(f"{message.author.display_name}: {message.content}")
            

