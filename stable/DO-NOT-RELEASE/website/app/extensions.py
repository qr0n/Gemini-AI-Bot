from functools import wraps
from flask import session, request, redirect, url_for, jsonify
import requests
import json
from pathlib import Path
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Discord OAuth2 credentials
CLIENT_ID = "1336834527951192134"
CLIENT_SECRET = "5NA0Yh11FgHhH8o8H8yF_6AYSBgltizK"
REDIRECT_URI = "http://localhost:5000/auth/callback"
API_BASE_URL = "https://discord.com/api"
AUTHORIZATION_BASE_URL = "https://discord.com/api/oauth2/authorize"
TOKEN_URL = "https://discord.com/api/oauth2/token"

# Data storage paths
DATA_DIR = Path("data")
PERSONALITY_DATA_DIR = DATA_DIR / "personality_traits"
BOTS_FILE = DATA_DIR / "bots.json"
SETTINGS_DATA_DIR = DATA_DIR / "settings"

# Create data directories
DATA_DIR.mkdir(exist_ok=True)
PERSONALITY_DATA_DIR.mkdir(parents=True, exist_ok=True)
SETTINGS_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Initialize bots.json if it doesn't exist
if not BOTS_FILE.exists():
    with open(BOTS_FILE, "w") as f:
        json.dump([], f)


class Helpers:
    def requires_auth(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            # Check if "token" is in the session
            if "token" not in session:
                token = request.cookies.get("token")
                if token:
                    session["token"] = token
                else:
                    return redirect(url_for("login"))
            return func(*args, **kwargs)

        return decorated_function

    def get_user_data():
        headers = {"Authorization": f"Bearer {session['token']}"}
        response = requests.get(f"{API_BASE_URL}/users/@me", headers=headers)
        user_data = response.json()
        print("User data: ", user_data)
        return user_data

    def list_nuggets():
        try:
            if not BOTS_FILE.exists():
                logger.warning(
                    f"Bots file not found at {BOTS_FILE}, creating empty file"
                )
                with open(BOTS_FILE, "w") as f:
                    json.dump([], f)
                return []

            with open(BOTS_FILE, "r") as f:
                bots = json.load(f)
                logger.info(f"Successfully loaded {len(bots)} bots from {BOTS_FILE}")
                return bots
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding bots.json: {e}")
            return []
        except Exception as e:
            logger.error(f"Error loading bots: {e}")
            return []

    def save_nugget(bot_data):
        try:
            logger.info(f"Saving bot data: {bot_data}")
            bots = Helpers.list_nuggets()

            # Generate a unique alias if not provided
            if "alias" not in bot_data:
                bot_data["alias"] = str(uuid.uuid4())
                logger.info(f"Generated new alias for bot: {bot_data['alias']}")

            # Update existing bot or add new one
            updated = False
            for i, bot in enumerate(bots):
                if bot["name"] == bot_data["name"]:
                    bots[i].update(bot_data)
                    updated = True
                    logger.info(f"Updated existing bot: {bot_data['name']}")
                    break

            if not updated:
                bots.append(bot_data)
                logger.info(f"Added new bot: {bot_data['name']}")

            with open(BOTS_FILE, "w") as f:
                json.dump(bots, f, indent=4)
                logger.info(f"Successfully saved bots to {BOTS_FILE}")

            return True, bot_data["alias"]
        except Exception as e:
            logger.error(f"Error saving bot: {e}")
            return False, None

    def delete_nugget(bot_name):
        try:
            bots = Helpers.list_nuggets()
            bots = [b for b in bots if b["name"] != bot_name]

            with open(BOTS_FILE, "w") as f:
                json.dump(bots, f, indent=4)

            # Delete associated personality file if it exists
            personality_file = PERSONALITY_DATA_DIR / f"{bot_name}.json"
            if personality_file.exists():
                personality_file.unlink()

            return True
        except Exception as e:
            print(f"Error deleting bot: {e}")
            return False


# Initialize settings manager
from .utils.settings_manager import SettingsManager

settings_manager = SettingsManager(DATA_DIR)
