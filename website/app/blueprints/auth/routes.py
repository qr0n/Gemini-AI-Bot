from flask import (
    render_template,
    redirect,
    url_for,
    request,
    make_response,
    session,
    flash,
)
import requests
import logging
from . import auth_bp
from ...extensions import (
    API_BASE_URL,
    AUTHORIZATION_BASE_URL,
    CLIENT_ID,
    CLIENT_SECRET,
    REDIRECT_URI,
    TOKEN_URL,
)


@auth_bp.route("/login")
def login():
    # Add state parameter for security
    return redirect(
        f"{AUTHORIZATION_BASE_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify&prompt=consent"
    )


@auth_bp.route("/callback")
def callback():
    error = request.args.get("error")
    if error:
        logging.error(f"OAuth error: {error}")
        flash(f"Authentication error: {error}", "error")
        return redirect(url_for("main.index"))

    code = request.args.get("code")
    if not code:
        logging.error("No code received from Discord")
        flash("Authentication failed - no code received", "error")
        return redirect(url_for("main.index"))

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()
        response_data = response.json()

        token = response_data["access_token"]

        response = make_response(redirect(url_for("dashboard.home")))
        response.set_cookie("token", token)
        response.set_cookie("darkMode", "enabled")
        session["token"] = token

        return response

    except requests.exceptions.RequestException as e:
        logging.error(f"Token exchange failed: {str(e)}")
        logging.error(
            f"Response content: {response.content if 'response' in locals() else 'No response'}"
        )
        flash("Authentication failed - please try again", "error")
        return redirect(url_for("main.index"))
