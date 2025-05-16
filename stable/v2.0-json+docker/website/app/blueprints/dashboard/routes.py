from flask import render_template, redirect, url_for
from . import dashboard_bp
from ...extensions import Helpers


@dashboard_bp.route("/home")
@Helpers.requires_auth
def home():
    user_data = Helpers.get_user_data()
    print(user_data)
    return render_template(
        "dashboard/home.html",
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


@dashboard_bp.route("/<nugget>/dashboard")
def dashboard(nugget):
    # simulate getting a query from the sql backend now we need to get that sql query
    client_id = 1245921609433481236
    return render_template(
        "dashboard/analytics-page.html",
        invite_url=f"https://discord.com/oauth2/authorize?client_id={client_id}&permissions=36809024&integration_type=0&scope=bot",
        nugget_alias=nugget,
    )


@dashboard_bp.route("/settings")
@Helpers.requires_auth
def settings():
    user_data = Helpers.get_user_data()
    return render_template(
        "dashboard/settings.html",
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
        invite_url="https://discord.com/oauth2/authorize?client_id={CL}&permissions=36809024&integration_type=0&scope=bot",
    )


@dashboard_bp.route("/<nugget>/model-configuration")
@Helpers.requires_auth
def model_conf(nugget):
    user_data = Helpers.get_user_data()

    return render_template(
        "dashboard/model-config.html",
        nugget_alias=nugget,
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
        invite_url="https://discord.com/oauth2/authorize?client_id={CL}&permissions=36809024&integration_type=0&scope=bot",
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
        invite_url="https://discord.com/oauth2/authorize?client_id={CL}&permissions=36809024&integration_type=0&scope=bot",
    )
