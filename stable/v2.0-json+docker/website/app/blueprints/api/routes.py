from flask import Blueprint, jsonify, request
from ...extensions import Helpers, PERSONALITY_DATA_DIR, db
from mysql.connector import Error
import json
import datetime
import uuid

from . import api_bp


@api_bp.route("/<nugget>/personality", methods=["GET"])
@Helpers.requires_auth
def get_personality(nugget):
    try:
        # Get from database
        database = Helpers.get_db()
        if not database:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = database.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT personality_traits.*
            FROM personality_traits
            JOIN bots ON bots.id = personality_traits.id
            WHERE bots.alias = %s
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


@api_bp.route("/<nugget>/personality", methods=["POST"])
@Helpers.requires_auth
def save_personality(nugget):
    try:
        data = request.json

        # Save to database
        database = Helpers.get_db()
        if not database:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = database.cursor()

        # Get bot_id
        cursor.execute("SELECT id FROM bots WHERE alias = %s", (nugget,))
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
                    "last_updated": datetime.datetime.now().isoformat(),
                },
                f,
                indent=4,
            )

        return jsonify({"success": True})
    except Error as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/bots", methods=["POST"])
@Helpers.requires_auth
def add_bot():
    try:
        data = request.json
        database = Helpers.get_db()
        uid = str(uuid.uuid4())
        if not database:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = database.cursor()
        cursor.execute(
            """
            INSERT INTO bots (discord_id, name, alias, avatar_url)
            VALUES (%s, %s, %s, %s)
            """,
            (data["discord_id"], data["bot_name"], uid, data.get("avatar_url")),
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
                    "uuid": uid,
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


@api_bp.route("/bots/<bot_name>", methods=["DELETE"])
@Helpers.requires_auth
def delete_bot(bot_name):
    try:
        database = Helpers.get_db()
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
