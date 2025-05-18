from flask import Blueprint, jsonify, request, render_template

from . import landing_bp


@landing_bp.route("/")
def landing():
    return render_template("auth/landing-page.html")
