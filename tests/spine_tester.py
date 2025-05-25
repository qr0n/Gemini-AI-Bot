# spine_tester.py
import requests
import json

BASE_URL = "http://localhost:56292"  # change this to your actual spine URL


def test_health():
    print("🩺 Testing /health...")
    r = requests.get(f"{BASE_URL}/hesalth")
    print("Status Code:", r.status_code)
    print("Response:", r.text)


def test_update_config(bot_id: str, new_config: dict):
    print("⚙️ Testing /update-config...")
    payload = {"bot_id": bot_id, "config": new_config}
    r = requests.post(f"{BASE_URL}/update-config", json=payload)
    print("Status Code:", r.status_code)
    print("Response:", r.text)


def test_event(bot_url: str, event_type: str):
    print("📡 Testing /event...")
    if event_type == "update_config":
        with open("test_config.json", "r") as json_file:
            try:
                config = json.load(json_file)
                payload = {"type": event_type, "config": config}
            except json.JSONDecodeError:
                print("❌ Invalid JSON.")
    if event_type == "update_personality":
        with open("test_partial_personality.json", "r") as json_file:
            try:
                personality = json.load(json_file)
                payload = {"type": event_type, "personality": personality}
            except json.JSONDecodeError:
                print("❌ Invalid JSON.")

    r = requests.post(f"{bot_url}/event", json=payload)
    print("Status Code:", r.status_code)
    print("Response:", r.text)


if __name__ == "__main__":
    # 🔁 Simple interactive menu
    while True:
        print("\nChoose test:")
        print("1. Test /health")
        print("2. Test /update-config")
        print("3. Test /event")
        print("4. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            test_health()
        elif choice == "2":
            bot_id = input("Enter bot ID: ")
            raw_config = input("Enter new config as JSON: ")
            try:
                config = json.loads(raw_config)
                test_update_config(bot_id, config)
            except json.JSONDecodeError:
                print("❌ Invalid JSON.")
        elif choice == "3":
            bot_url = input(f"Enter bot URL (e.g. {BASE_URL}): ") or BASE_URL
            event_type = input("Enter event type (e.g. shutdown, restart_session): ")
            test_event(bot_url, event_type)

        elif choice == "4":
            break
        else:
            print("Invalid choice.")
