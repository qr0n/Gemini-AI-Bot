from flask import jsonify, request
from . import api_bp
from ...extensions import Helpers, settings_manager


@api_bp.route("/settings/<nugget>/<category>", methods=["GET"])
@Helpers.requires_auth
def get_settings(nugget, category):
    """Get settings for a specific nugget and category."""
    try:
        settings = settings_manager.get_settings(nugget, category)
        return jsonify(settings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/settings/<nugget>/<category>", methods=["POST"])
@Helpers.requires_auth
def save_settings(nugget, category):
    """Save settings for a specific nugget and category."""
    try:
        settings = request.json
        if settings_manager.save_settings(nugget, category, settings):
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Failed to save settings"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/settings/<nugget>/<category>/reset", methods=["POST"])
@Helpers.requires_auth
def reset_settings(nugget, category):
    """Reset settings to defaults for a specific nugget and category."""
    try:
        defaults = settings_manager.reset_settings(nugget, category)
        return jsonify(defaults)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/validate-key", methods=["POST"])
@Helpers.requires_auth
def validate_api_key():
    """Validate an API key."""
    try:
        data = request.json
        key = data.get("key")
        service = data.get("service")

        if not key or not service:
            return jsonify({"error": "Missing key or service"}), 400

        is_valid = settings_manager.validate_api_key(key, service)
        return jsonify({"valid": is_valid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
