"""
This is an optimization file created 
to supply the other modules/cogs with functions/classes that are frequently called

Optimization 1:
    Reduce definitions of X.load_character_details()

Optimization 2:
    Reduce definitions of config

"""

import json


class CommonCalls:

    def load_character_details():
        """
        Description -
        Handles the `prompt.json` and returns the personality details.

        Arguments -
        None

        Returns -
        Dict[str, str]
        """
        try:
            with open("prompt.json", "r") as unloaded_prompt_json:
                prompt_json = json.load(unloaded_prompt_json)

        except FileNotFoundError:
            raise FileNotFoundError("The prompt.json file was not found.")

        except json.JSONDecodeError:
            raise ValueError("The prompt.json file is not a valid JSON.")

        personality_traits = prompt_json.get("personality_traits", {})

        name = personality_traits.get("name", "unknown_bot")
        role = personality_traits.get("role", "unknown_role")

        age = personality_traits.get("age", "unknown_age")
        description = personality_traits.get("description", "no description provided")

        likes = personality_traits.get("likes", "N/A")
        dislikes = personality_traits.get("dislikes", "N/A")

        return {
            "name": name,
            "role": role,
            "age": age,
            "description": description,
            "likes": likes,
            "dislikes": dislikes,
        }

    def config():
        with open("./config.json", "r") as ul_config:
            return json.load(ul_config)

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
