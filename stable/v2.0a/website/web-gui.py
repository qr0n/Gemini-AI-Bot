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

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Discord OAuth2 credentials
CLIENT_ID = ""
CLIENT_SECRET = ""
REDIRECT_URI = "http://localhost:5000/callback"
API_BASE_URL = "https://discord.com/api"
AUTHORIZATION_BASE_URL = "https://discord.com/api/oauth2/authorize"
TOKEN_URL = "https://discord.com/api/oauth2/token"


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
    response = make_response(redirect(url_for("profile")))
    response.set_cookie("token", token)

    session["token"] = token
    return response


@app.route("/dashboard")
def profile():
    if "token" not in session:
        token = request.cookies.get("token")
        if token:
            session["token"] = token

        else:
            return redirect(url_for("login"))

        return redirect(url_for("login"))

    headers = {"Authorization": f"Bearer {session['token']}"}
    response = requests.get(f"{API_BASE_URL}/users/@me", headers=headers)
    user_data = response.json()
    print("User data: ", user_data)
    return render_template(
        "nugget-config.html",
        username=user_data["username"],
        avatar_url=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png",
    )


if __name__ == "__main__":
    app.run(debug=True)
