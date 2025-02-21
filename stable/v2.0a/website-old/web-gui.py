from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    session,
    make_response,
    send_from_directory,
    abort,
    jsonify,
)

import os
import requests
import mysql.connector
import json
import datetime

from pathlib import Path
from functools import wraps
from helpers import Helpers
from mysql.connector import Error
from database import Database

app = Flask(__name__)u,k.ol9
app.secret_key = os.urandom(24)

# Discord OAuth2 credentials
CLIENT_ID = "1336834527951192134"
CLIENT_SECRET = "5NA0Yh11FgHhH8o8H8yF_6AYSBgltizK"
REDIRECT_URI = "http://localhost:5000/callback"
API_BASE_URL = "https://discord.com/api"
AUTHORIZATION_BASE_URL = "https://discord.com/api/oauth2/authorize"
TOKEN_URL = "https://discord.com/api/oauth2/token"

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Replace with your username
    password="iron",  # Replace with your password
    database="bot_memory",  # Specify the database
)

PERSONALITY_DATA_DIR = Path("data/personality_traits")
PERSONALITY_DATA_DIR.mkdir(parents=True, exist_ok=True)

cursor = db.cursor()


@app.route("/")
def landing_page():
    return render_template("landing-page.html")


@app.route("/static/<file>")
def js_getter(file):
    try:
        return send_from_directory("static", file)
    except FileNotFoundError:
        return abort(404)


@app.route("/login")
def login():
    return redirect(
        f"{AUTHORIZATION_BASE_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify"
    )


# https://discord.com/api/oauth2/authorize?client_id=1336834527951192134&response_type=code&redirect_uri=
# https://discord.com/oauth2/authorize?client_id=1336834527951192134&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fprofile&scope=identify+email


@app.route("/callback")
def callback():
    code = request.args.get("code")
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(TOKEN_URL, data=data, headers=headers)
    response_data = response.json()
    token = response_data["access_token"]

    # Set the token in a cookie
    response = make_response(redirect(url_for("home")))
    response.set_cookie("token", token)
    response.set_cookie("darkMode", "enabled")

    session["token"] = token

    return response


@app.route("/home")
@Helpers.Helpers.requires_auth
def home():
    user_data = Helpers.get_user_data()
    return render_template(
        "home.html",
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
        # nuggets=[
        #     {
        #         "image_url": f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
        #         "name": "Nugget 1",
        #         "alias": "sponge-mk7",
        #     },
        #     {
        #         "image_url": f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
        #         "name": "Nugget 2",
        #     },
        #     # Add more nugget objects as needed
        # ],
        nuggets=Helpers.list_nuggets(),
    )  # TODO : get data from db


@app.route("/<nugget>/dashboard")
def dashboard(nugget):
    # simulate getting a query from the sql backend now we need to get that sql query
    client_id = 1245921609433481236
    return render_template(
        "analytics-page.html",
        invite_url=f"https://discord.com/oauth2/authorize?client_id={client_id}&permissions=36809024&integration_type=0&scope=bot",
        nugget_alias=nugget,
    )


@app.route("/settings")
@Helpers.Helpers.requires_auth
def settings():
    user_data = Helpers.get_user_data()
    return render_template(
        "settings.html",
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


@app.route("/<nugget>/memories")
@Helpers.requires_auth
def memories(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "memories.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
        invite_url="https://discord.com/oauth2/authorize?client_id={CL}&permissions=36809024&integration_type=0&scope=bot",
    )


@app.route("/<nugget>/model-configuration")
@Helpers.requires_auth
def model_conf(nugget):
    user_data = Helpers.get_user_data()

    return render_template(
        "model-config.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
        invite_url="https://discord.com/oauth2/authorize?client_id={CL}&permissions=36809024&integration_type=0&scope=bot",
    )


@app.route("/<nugget>/knowledge")
@Helpers.requires_auth
def knowledge(nugget):
    user_data = Helpers.get_user_data()

    return render_template(
        "knowledge.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
        invite_url="https://discord.com/oauth2/authorize?client_id={CL}&permissions=36809024&integration_type=0&scope=bot",
    )


@app.route("/api/<nugget>/personality", methods=["GET"])
@Helpers.requires_auth
def get_personality(nugget):
    try:
        # Get from database
        database = Database.get_db()
        if not database:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = database.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT pt.* FROM personality_traits pt
            JOIN bots b ON b.id = pt.bot_id
            WHERE b.name = %s
        """,
            (nugget,),
        )
        traits = cursor.fetchone()
        cursor.close()

        # Also save/update JSON file
        json_path = PERSONALITY_DATA_DIR / f"{nugget}.json"
        if traits:
            with open(json_path, "w") as f:
                json.dump(traits, f, indent=4)
        elif json_path.exists():
            with open(json_path, "r") as f:
                traits = json.load(f)

        return jsonify(traits if traits else {})
    except Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/<nugget>/personality", methods=["POST"])
@Helpers.requires_auth
def save_personality(nugget):
    try:
        data = request.json

        # Save to database
        database = Database.get_db()
        if not database:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = database.cursor()

        # Get bot_id
        cursor.execute("SELECT id FROM bots WHERE name = %s", (nugget,))
        bot = cursor.fetchone()
        if not bot:
            return jsonify({"error": "Bot not found"}), 404

        bot_id = bot[0]

        # Update or insert personality traits
        cursor.execute(
            """
            INSERT INTO personality_traits 
            (bot_id, name, age, role, description, likes, dislikes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            age = VALUES(age),
            role = VALUES(role),
            description = VALUES(description),
            likes = VALUES(likes),
            dislikes = VALUES(dislikes)
        """,
            (
                bot_id,
                data["name"],
                data["age"],
                data["role"],
                data["description"],
                data["likes"],
                data["dislikes"],
            ),
        )

        db.commit()
        cursor.close()

        # Also save to JSON file
        json_path = PERSONALITY_DATA_DIR / f"{nugget}.json"
        with open(json_path, "w") as f:
            json.dump(
                {
                    "bot_name": nugget,
                    "name": data["name"],
                    "age": data["age"],
                    "role": data["role"],
                    "description": data["description"],
                    "likes": data["likes"],
                    "dislikes": data["dislikes"],
                    "last_updated": datetime.now().isoformat(),
                },
                f,
                indent=4,
            )

        return jsonify({"success": True})
    except Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/bots", methods=["POST"])
@Helpers.requires_auth
def add_bot():
    try:
        data = request.json
        database = Database.get_db()
        if not database:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = database.cursor()
        cursor.execute(
            """
            INSERT INTO bots (discord_id, name, avatar_url)
            VALUES (%s, %s, %s)
            """,
            (data["discord_id"], data["bot_name"], data.get("avatar_url")),
        )
        database.commit()
        bot_id = cursor.lastrowid
        cursor.close()

        # Create empty personality file
        json_path = PERSONALITY_DATA_DIR / f"{data['bot_name']}.json"
        with open(json_path, "w") as f:
            json.dump(
                {
                    "bot_name": data["bot_name"],
                    "name": "",
                    "age": "",
                    "role": "",
                    "description": "",
                    "likes": "",
                    "dislikes": "",
                    "last_updated": datetime.datetime.now().isoformat(),
                },
                f,
                indent=4,
            )

        return jsonify({"success": True, "id": bot_id})
    except Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/bots/<bot_name>", methods=["DELETE"])
@Helpers.requires_auth
def delete_bot(bot_name):
    try:
        database = Database.get_db()
        if not database:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = database.cursor()
        cursor.execute("DELETE FROM bots WHERE name = %s", (bot_name,))
        database.commit()
        cursor.close()

        # Delete personality file if exists
        json_path = PERSONALITY_DATA_DIR / f"{bot_name}.json"
        if json_path.exists():
            json_path.unlink()

        return jsonify({"success": True})
    except Error as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
