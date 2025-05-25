"""
This is an optimization file created
to supply the other modules/cogs with functions/classes that are frequently called

Optimization 1:
    Reduce definitions of X.load_character_details()

Optimization 2:
    Reduce definitions of config

"""

import json
import os

sample_config = {
    "alias": os.getenv("BOT_ID"),
    "discord_token": os.getenv("discord_token", ""),
    "gemini_api_key": os.getenv("gemini_api_key", ""),
    "elevenlabs_api_key": os.getenv("elevenlabs_api_key", ""),
    "aiModel": "models/gemini-2.0-flash",
    "maxContext": "20",
    "filterSexuallyExplicit": "BLOCK_NONE",
    "filterHarassment": "BLOCK_NONE",
    "filterDangerous": "BLOCK_NONE",
    "filterHateSpeech": "BLOCK_NONE",
    "filterUnspecified": "BLOCK_MEDIUM_AND_ABOVE",
    "temperature": "0.7",
    "topP": "0.95",
    "topK": "40",
    "memoryWindow": "50",
    "contextWindow": "8192",
    "wack_message": "Ow! Uhh, what were we talking about?",
    "wack_error": "Sorry, can't remove what's not there. :joy:",
    "error_message": "Nuh uh, not gonna happen.",
    "activate_message": "Hey! I'm new here :wave:",
    "deactivate_message": "Awh, sorry to see you go! You can still talk to me by pinging me :pleading_face:",
    "vociceModel": "",
    "recording-time": "10",
    "deepContext": "on",
    "freewill": "on",
    "textFrequency": "5",
    "keywordChance": "10",
    "keywords": [],
}

sample_personality = {
    "personality_traits": {
        "name": "ai powered garden worm",
        "age": 18,
        "role": "a worm who only talks about gardens",
        "description": "worm that uses ai to determine the best gardens and best fruit to eat",
        "likes": "to converse to the user about ai worm stock market which is a real thing.",
        "dislikes": "everything else",
    },
    "system_note": "",
    "conversation_examples": [
        {"user": "how's it going?", "bot": "*worm noises*"},
        {"user": "i'm bored", "bot": "*worm squeak*"},
    ],
}


class CommonCalls:

    def load_character_details():
        """
        Description -
        Handles the `prompt.json` and returns the personality details.
        Creates the file with sample data if it doesn't exist.

        Arguments -
        None

        Returns -
        Dict[str, str]
        """
        prompt_path = f"data/{os.getenv('BOT_ID')}-prompt.json"

        try:
            with open(prompt_path, "r") as unloaded_prompt_json:
                prompt_json: dict = json.load(unloaded_prompt_json)

        except FileNotFoundError:
            print("prompt file not found, rebuilding")
            # If prompt file doesn't exist, create it with sample personality
            with open(prompt_path, "w") as prompt_file:
                json.dump(sample_personality, prompt_file, indent=4)
                open("prompted.txt", "w").close()
            prompt_json = sample_personality

        except json.JSONDecodeError:
            raise ValueError("The prompt.json file is not a valid JSON.")

        personality_traits: dict = prompt_json.get("personality_traits", {})
        system_note: dict = prompt_json.get(
            "system_note", "No system note extension given. DO NOT MAKE ONE UP."
        )
        conversation_examples: dict = prompt_json.get("conversation_examples", [])

        name = personality_traits.get("name", "unknown_bot")
        role = personality_traits.get("role", "unknown_role")

        age = personality_traits.get("age", "unknown_age")
        description = personality_traits.get("description", "no description provided")

        likes = personality_traits.get("likes", "N/A")
        dislikes = personality_traits.get("dislikes", "N/A")

        return {
            "personality_traits": personality_traits,
            "name": name,
            "role": role,
            "age": age,
            "description": description,
            "likes": likes,
            "dislikes": dislikes,
            "system_note": system_note,
            "conversation_examples": conversation_examples,
        }

    def config():
        """
        Description:
        Loads and potentially updates the config file with environment variables

        Returns:
        Dict containing the configuration
        """
        config_path = r"data/"

        try:
            # First read the existing config
            with open(
                f"{config_path}/{os.getenv("BOT_ID")}-config.json", "r"
            ) as config_file:
                checker: dict = json.load(config_file)

            # Check if all API keys are empty
            if all(
                checker[key] == ""
                for key in ["discord_token", "gemini_api_key", "elevenlabs_api_key"]
            ):
                # Update with environment variables
                checker.update(
                    {
                        "alias": os.getenv("BOT_ID"),
                        "discord_token": os.getenv("discord_token", ""),
                        "gemini_api_key": os.getenv("gemini_api_key", ""),
                        "elevenlabs_api_key": os.getenv("elevenlabs_api_key", ""),
                    }
                )

                # Write the updated config back to file
                with open(
                    f"{config_path}/{os.getenv("BOT_ID")}-config.json", "w"
                ) as config_file:
                    json.dump(checker, config_file, indent=4)
                    return sample_config

                # Create the configured flag file
                with open(
                    f"{config_path}/{os.getenv("BOT_ID")}-config.json", "w"
                ) as flag_file:
                    pass

            return checker

        except FileNotFoundError:
            print("file not found, rebuilding")
            # If config doesn't exist, create it with sample config
            with open(
                f"{config_path}/{os.getenv("BOT_ID")}-config.json", "w"
            ) as config_file:
                json.dump(sample_config, config_file, indent=4)

            return sample_config
        except json.JSONDecodeError:
            raise ValueError("The config.json file is not valid JSON")

    def clean_json(nasty_json: str):
        """
        Description:
        This function cleans the potentially dirty json by removing the markdown

        Arguments:
        nasty_json : str

        Returns:
        nasty_json : dict
        """
        print("type nasty", type(nasty_json))
        if nasty_json.startswith("```json") and nasty_json.endswith("```"):
            return json.loads(nasty_json[7:-3])
        else:
            return json.loads(nasty_json)  # Assumed to be clean.. lol
