import json
from discord.ext import commands
from discord import Intents, Message
import os

with open("config.json", "r") as _config:
    config = json.load(_config)

intents = Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)

@bot.event
async def setup_hook():
    for filename in os.listdir('D:/Python/Gemini-AI-Bot/v0.9/cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(config["BOT_TOKEN"])