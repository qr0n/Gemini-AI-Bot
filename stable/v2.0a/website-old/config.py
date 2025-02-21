import os


class Config:
    SECRET_KEY = os.urandom(24)

    # Discord OAuth2 credentials
    CLIENT_ID = ""
    CLIENT_SECRET = ""
    REDIRECT_URI = "http://localhost:5000/callback"
    API_BASE_URL = "https://discord.com/api"
    AUTHORIZATION_BASE_URL = "https://discord.com/api/oauth2/authorize"
    TOKEN_URL = "https://discord.com/api/oauth2/token"

    # Database config
    DB_HOST = "localhost"
    DB_USER = "root"
    DB_PASS = "iron"
    DB_NAME = "bot_memory"

    # Paths
    PERSONALITY_DATA_DIR = "data/personality_traits"
