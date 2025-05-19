from flask import render_template, redirect, url_for, request
from . import dashboard_bp
from ...extensions import Helpers
import logging

logger = logging.getLogger(__name__)


# Main routes
@dashboard_bp.route("/home")
@Helpers.requires_auth
def home():
    try:
        user_data = Helpers.get_user_data()
        nuggets = Helpers.list_nuggets()
        logger.info(f"Loaded {len(nuggets)} bots for user {user_data['username']}")

        return render_template(
            "dashboard/home.html",
            username=user_data["username"],
            avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
            nuggets=nuggets,
        )
    except Exception as e:
        logger.error(f"Error in home route: {e}")
        return render_template(
            "dashboard/home.html",
            username="User",
            avatar_url="https://cdn.discordapp.com/embed/avatars/0.png",
            nuggets=[],
            error="Failed to load bots. Please try again later.",
        )


# Bot-specific routes
@dashboard_bp.route("/<nugget>/dashboard")
@Helpers.requires_auth
def dashboard(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "dashboard/analytics-page.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


@dashboard_bp.route("/<nugget>/settings")
@Helpers.requires_auth
def settings(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "dashboard/settings.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


@dashboard_bp.route("/<nugget>/memories")
@Helpers.requires_auth
def memories(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "dashboard/memories.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


@dashboard_bp.route("/<nugget>/model-configuration")
@Helpers.requires_auth
def model_config(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "dashboard/model-config.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


@dashboard_bp.route("/<nugget>/knowledge")
@Helpers.requires_auth
def knowledge(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "dashboard/knowledge.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


# AI routes
@dashboard_bp.route("/<nugget>/ai/filters")
@Helpers.requires_auth
def ai_filters(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "dashboard/ai/filters.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


@dashboard_bp.route("/<nugget>/ai/generation")
@Helpers.requires_auth
def ai_generation(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "dashboard/ai/generation.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


@dashboard_bp.route("/<nugget>/ai/model")
@Helpers.requires_auth
def ai_model(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "dashboard/ai/model.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


@dashboard_bp.route("/<nugget>/ai/prompting")
@Helpers.requires_auth
def prompting(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "dashboard/ai/prompting.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


@dashboard_bp.route("/<nugget>/ai/messages")
@Helpers.requires_auth
def ai_messages(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "dashboard/ai/messages.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


# Personality routes
@dashboard_bp.route("/<nugget>/personality/traits")
@Helpers.requires_auth
def personality_traits(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "dashboard/personality/traits.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


@dashboard_bp.route("/<nugget>/personality/prompting")
@Helpers.requires_auth
def personality_prompting(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "dashboard/personality/prompting.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


@dashboard_bp.route("/<nugget>/personality/autonomy")
@Helpers.requires_auth
def personality_autonomy(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "dashboard/personality/autonomy.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


# Features routes
@dashboard_bp.route("/<nugget>/features/agent")
@Helpers.requires_auth
def features_agent(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "dashboard/features/agent.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


@dashboard_bp.route("/<nugget>/features/files")
@Helpers.requires_auth
def features_files(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "dashboard/features/files.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


@dashboard_bp.route("/<nugget>/features/voice")
@Helpers.requires_auth
def features_voice(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "dashboard/features/voice.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


@dashboard_bp.route("/<nugget>/api-keys", methods=["GET", "POST"])
@Helpers.requires_auth
def api_keys(nugget):
    if request.method == "GET":
        user_data = Helpers.get_user_data()
        return render_template(
            "dashboard/authentication/api-keys.html",
            nugget_alias=nugget,
            username=user_data["username"],
            avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
        )
    if request.method == "POST":
        print(request.args)
        return "hello"
