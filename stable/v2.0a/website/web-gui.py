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
)
import os
import requests
from functools import wraps
from helpers import Helpers

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Discord OAuth2 credentials


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


@app.route("/")
def home():
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
    response = make_response(redirect(url_for("dashboard")))
    response.set_cookie("token", token)
    response.set_cookie("darkMode", "enabled")

    session["token"] = token

    return response


@app.route("/dashboard")
@Helpers.requires_auth
def dashboard():
    user_data = Helpers.get_user_data()
    return render_template(
        "home.html",
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
        nuggets=[
            {
                "image_url": f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
                "name": "Nugget 1",
            },
            {
                "image_url": f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
                "name": "Nugget 2",
            },
            # Add more nugget objects as needed
        ],
    )


@app.route("/<nugget>/settings")
@requires_auth
def settings(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "settings.html",
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
        invite_url="https://discord.com/oauth2/authorize?client_id={CL}&permissions=36809024&integration_type=0&scope=bot",
    )


@app.route("/<nugget>/memories")
@requires_auth
def memories(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "knowledge.html",
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
        invite_url="https://discord.com/oauth2/authorize?client_id={CL}&permissions=36809024&integration_type=0&scope=bot",
    )


@app.route("/render/<file>")
def render(file):
    return render_template(file)


if __name__ == "__main__":
    app.run(debug=True)
