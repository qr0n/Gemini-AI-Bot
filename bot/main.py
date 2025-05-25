# main.py
import os, threading
from discord.ext import commands
from discord import Intents
import uvicorn
from spine_server import create_app  # as we defined it
from modules.CommonCalls import CommonCalls

intents = Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

mem_path = f"data/{CommonCalls.config()['alias']}-memories.json"
act_path = f"data/{CommonCalls.config()['alias']}-activation.json"


@bot.listen("on_ready")
async def load_cogs():
    for ext in os.listdir("cogs"):
        if ext.endswith(".py"):
            bot.load_extension(f"cogs.{ext[:-3]}")
    try:
        with open(mem_path, "r") as file:
            file.close()
    except FileNotFoundError:
        with open(mem_path, "w") as file:
            file.write("{}")
            file.close()
    try:
        with open(act_path, "r") as file:
            file.close()
    except FileNotFoundError:
        with open(act_path, "w") as file:
            file.write("{}")
            file.close()


def start_api():
    app = create_app(bot)
    # uvicorn.run will create and manage its own event loop
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    # 1) start FastAPI in its own thread
    t = threading.Thread(target=start_api, daemon=True)
    t.start()

    # 2) start your Discord bot (blocks, uses its own loop)
    bot.run(CommonCalls.config()["discord_token"])
