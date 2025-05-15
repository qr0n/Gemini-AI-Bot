import json
import os
from discord.ext import commands
from discord import Intents, Message

with open("config.json", "r") as _config:
    config = json.load(_config)

intents = Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.listen("on_ready", once=True)
async def load_cogs():
    # This is an asynchronous function called 'load_cogs'
    # this function is called everytime the bot is initialized
    # NOTE: This CAN AND WILL HAPPEN MULTIPLE TIMES DURING THE CYCLE
    # NOTE: THIS IS NOT RECOMMENDED TO BE UNDER .
    # for filename in os.listdir('D:/Python/Gemini-AI-Bot/v0.8-alpha-json/cogs'):
    for extension in os.listdir(os.getcwd() + "/cogs"):
        # This iterates through the folder
        # NOTE: Change the path to match your folder
        if extension.endswith(".py"):
            bot.load_extension(f"cogs.{extension[:-3]}")
            # Loads the extension(s)


# TODO:
# Apply CommonCalls everywhere and increase its coverage

# TODO:
# Add history builder

# TODO:
# Add web configuration

bot.run(config["BOT_TOKEN"])
