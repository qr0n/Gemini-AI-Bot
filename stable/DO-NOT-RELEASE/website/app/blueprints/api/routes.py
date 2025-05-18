from flask import Blueprint, jsonify, request
from ...extensions import Helpers, PERSONALITY_DATA_DIR
import json
import datetime

from . import api_bp


@api_bp.route("/<nugget>/personality", methods=["GET"])
@Helpers.requires_auth
def get_personality(nugget):
    try:
        json_path = PERSONALITY_DATA_DIR / f"{nugget}.json"
        if json_path.exists():
            with open(json_path, "r") as f:
                traits = json.load(f)
            return jsonify(traits)
        return jsonify({})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/<nugget>/personality", methods=["POST"])
@Helpers.requires_auth
def save_personality(nugget):
    try:
        data = request.json

        # Save to JSON file
        json_path = PERSONALITY_DATA_DIR / f"{nugget}.json"
        personality_data = {
            "bot_name": nugget,
            "name": data["name"],
            "age": data["age"],
            "role": data["role"],
            "description": data["description"],
            "likes": data["likes"],
            "dislikes": data["dislikes"],
            "last_updated": datetime.datetime.now().isoformat(),
        }

        with open(json_path, "w") as f:
            json.dump(personality_data, f, indent=4)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/bots", methods=["POST"])
@Helpers.requires_auth
def add_bot():
    try:
        data = request.json
        bot_data = {
            "name": data["bot_name"],
            "discord_id": data["discord_id"],
            "avatar_url": data.get("avatar_url", ""),
        }

        success, alias = Helpers.save_nugget(bot_data)
        if success:
            # Create empty personality file
            json_path = PERSONALITY_DATA_DIR / f"{data['bot_name']}.json"
            with open(json_path, "w") as f:
                json.dump(
                    {
                        "bot_name": data["bot_name"],
                        "alias": alias,
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

            return jsonify({"success": True, "alias": alias})
        else:
            return jsonify({"error": "Failed to save bot"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/bots/<bot_name>", methods=["DELETE"])
@Helpers.requires_auth
def delete_bot(bot_name):
    try:
        if Helpers.delete_nugget(bot_name):
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Failed to delete bot"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
