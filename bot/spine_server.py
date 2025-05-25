from fastapi import FastAPI, Request, HTTPException
from discord.ext import commands
import asyncio
import json
import os


def create_app(bot: commands.Bot):
    app = FastAPI()

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.post("/event")
    async def event_trigger(request: Request):
        data: dict = await request.json()
        match data.get("type"):
            case "update_config":
                config = data.get("config")
                print("[SPINE SERVER] [CRITICAL] | Analyzing config")
                print(config)
                print("updating config keys... please hold")
                config_path = f"/app/data/{os.getenv('BOT_ID')}-config.json"

                # Read existing config
                existing_config = {}
                if os.path.exists(config_path):
                    try:
                        with open(config_path, "r") as f:
                            existing_config = json.load(f)
                    except json.JSONDecodeError:
                        print(
                            "[SPINE SERVER] [WARNING] | Existing config file is invalid JSON"
                        )

                # Update only the provided keys
                existing_config.update(config)

                # Save updated config
                with open(config_path, "w") as f:
                    json.dump(existing_config, f, indent=4)
                return {"status": "config updated"}

            case "update_personality":
                personality = data.get("personality")
                print("[SPINE SERVER] [CRITICAL] | Analyzing personality")
                print(f"Type: {type(personality)}")
                print(personality)
                print("updating personality keys... please hold")
                prompt_path = f"/app/data/{os.getenv('BOT_ID')}-prompt.json"

                # Read existing personality
                existing_personality = {}
                if os.path.exists(prompt_path):
                    try:
                        with open(prompt_path, "r") as f:
                            existing_personality = json.load(f)
                    except json.JSONDecodeError:
                        print(
                            "[SPINE SERVER] [WARNING] | Existing personality file is invalid JSON"
                        )

                # Update only the provided keys
                existing_personality.update(personality)

                # Save updated personality
                with open(prompt_path, "w") as f:
                    json.dump(existing_personality, f, indent=4)
                return {"status": "personality updated"}

            case _:
                return {"status": "unknown event"}

    return app


async def start_web(bot, config):
    from uvicorn import Config, Server

    app = create_app(bot, config)
    server = Server(
        Config(app, host="0.0.0.0", port=8000, loop="asyncio", log_level="info")
    )
    await server.serve()
