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
CLIENT_ID = "1336834527951192134"
CLIENT_SECRET = "5NA0Yh11FgHhH8o8H8yF_6AYSBgltizK"
REDIRECT_URI = "http://localhost:5000/callback"
API_BASE_URL = "https://discord.com/api"
AUTHORIZATION_BASE_URL = "https://discord.com/api/oauth2/authorize"
TOKEN_URL = "https://discord.com/api/oauth2/token"


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
@Helpers.requires_auth
def home():
    user_data = Helpers.get_user_data()
    return render_template(
        "home.html",
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
        nuggets=[
            {
                "image_url": f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
                "name": "Nugget 1",
                "alias": "sponge-mk7",
            },
            {
                "image_url": f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
                "name": "Nugget 2",
            },
            # Add more nugget objects as needed
        ],
    )


@app.route("/<nugget>/dashboard")
def dashboard(nugget):
    # simulate getting a query from the sql backend
    client_id = 1245921609433481236
    user_data = Helpers.get_user_data()
    return render_template(
        "analytics-page.html",
        invite_url=f"https://discord.com/oauth2/authorize?client_id={client_id}&permissions=36809024&integration_type=0&scope=bot",
        nugget_alias=nugget,
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


@app.route("/settings")
@requires_auth
def settings():
    user_data = Helpers.get_user_data()
    return render_template(
        "settings.html",
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


@app.route("/<nugget>/memories")
@requires_auth
def memories(nugget):
    user_data = Helpers.get_user_data()
    return render_template(
        "memories.html",
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
        invite_url="https://discord.com/oauth2/authorize?client_id={CL}&permissions=36809024&integration_type=0&scope=bot",
        bot_memories=[
            {
                "special_phrase": "the dog jumped over the boy's moon and the lazy brown fox watched.",
                "content": "Jason goes on this adventure where he aquires a moon on his planet. a huge dog spiteful and evil decicded jason's moon was stealing the attention from him so he jumped over the boys moon, the wise brown fox was lazy and just watched.",
            },
            {
                "special_phrase": "the dog jumped over the boy's moon and the lazy brown fox watched."
            },
        ],
    )


@app.route("/render/<file>")
def render(file):
    return render_template(file)


if __name__ == "__main__":
    app.run(debug=True)
