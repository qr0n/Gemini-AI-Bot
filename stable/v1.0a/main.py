import json
import os
from discord.ext import commands
from discord import Intents, Message
import discord

with open("config.json", "r") as _config:
    config = json.load(_config)

intents = Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.listen("on_ready", once=True)
async def cog_loader():
    await bot.change_presence(status=discord.Status.idle)
    print("Loading extentions")
    for filename in os.listdir(os.getcwd() + "/cogs"):
        if filename.endswith(".py"):
            print("loading [", filename, "]")
            bot.load_extension(f"cogs.{filename[:-3]}")


bot.run(config["BOT_TOKEN"])
