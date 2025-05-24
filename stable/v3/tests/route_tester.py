import requests

# Change this to match your running server address
BASE_URL = "http://localhost:5000/api/bots"


def test_add_bot():
    payload = {
        "bot_name": "gold nugget",
        "discord_token": "",
        "avatar_url": "",
        "gemini_api_key": "",
        "elevenlabs_api_key": "",
    }

    # If your endpoint requires an auth header (e.g., JWT):
    headers = {
        "Content-Type": "application/json",
        # "Authorization": "Bearer <your_token_here>"
    }

    response = requests.post(BASE_URL, json=payload, headers=headers)

    print("Status Code:", response.status_code)
    print("Response:", response.json())


if __name__ == "__main__":
    test_add_bot()
