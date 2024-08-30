# This file is reserved for the Discord Bot only.
# Everything else relating to Gemini will be abstracted by functions.

import json
from discord.ext import commands
from discord import Intents
import os

with open("config.json", "r") as _config:
    config = json.load(_config)

# This is opening a file called 'config.json' as _config
# config is now a globally defined variable that is being loaded from the file

intents = Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)

@bot.listen("on_ready")
async def load_cogs():
    # This is an asynchronous function called 'load_cogs'
    # this function is called everytime the bot is initialized
    # NOTE: This CAN AND WILL HAPPEN MULTIPLE TIMES DURING THE CYCLE
    # NOTE: THIS IS NOT RECOMMENDED TO BE UNDER .
    for filename in os.listdir('D:/Python/Gemini-AI-Bot/v0.8-alpha-json/cogs'):
        # This iterates through the folder
        # NOTE: Change the path to match your folder
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            # Loads the extension(s)

bot.run(config["BOT_TOKEN"])