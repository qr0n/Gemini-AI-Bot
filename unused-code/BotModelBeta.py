import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json
# from modules.Memories import Memories
from discord import Message
from PIL import Image

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

# context_window = ContextWindow() # TODO : Reimplement ContextWindow

genai.configure(api_key=config["API_KEY"])

def load_character_details():
    """
    `load_character_details`
    Takes no arguments, returns dictionary
    name : str
    role : str
    age : int
    description : str
    """
    try:
        with open("prompt.json", "r") as unloaded_prompt_json:
            prompt_json = json.load(unloaded_prompt_json)
    except FileNotFoundError:
        raise FileNotFoundError("The prompt.json file was not found.")
    except json.JSONDecodeError:
        raise ValueError("The prompt.json file is not a valid JSON.")
    personality_traits = prompt_json.get('personality_traits', {})
    name = personality_traits.get('name', 'unknown_bot')
    role = personality_traits.get('role', 'unknown_role')
    age = personality_traits.get('age', 'unknown_age')
    description = personality_traits.get('description', 'no description provided')

    return {
        "name": name,
        "role": role,
        "age": age,
        "description": description
    }

def read_prompt():
    try:
        with open("prompt.json", "r") as unloaded_prompt_json:
            prompt_json: dict = json.load(unloaded_prompt_json)
    except FileNotFoundError:
        raise FileNotFoundError("The prompt.json file was not found.")
    except json.JSONDecodeError:
        raise ValueError("The prompt.json file is not a valid JSON.")
    
    # Extract information from nested structure
    personality_traits: dict= prompt_json.get('personality_traits', {})
    system_note: dict = prompt_json.get('system_note', "No system note extension given. DO NOT MAKE ONE UP.")
    conversation_examples: dict = prompt_json.get('conversation_examples', [])
    
    # Specific traits
    name = personality_traits.get('name', 'unknown_bot')
    age = personality_traits.get('age', 'unknown_age')
    role = personality_traits.get('role', 'unknown_role')
    description = personality_traits.get('description', 'no description provided')
    author_name = "iron" #discord_message.author.name if discord_message else "unknown_user"
    bot_name = load_character_details()['name']
    
    system_instruction = f"""
    You are {name}, a {role}, {age} years old, described as {description}.
    You are conversing with {author_name}.
    Your job as {bot_name} is to respond to the last message from {author_name} appropriately.
    You can use the messages provided, but you may not ever directly reference them.
    """
    
    return system_instruction

model = genai.GenerativeModel(model_name=config["AI_MODEL"], system_instruction=read_prompt())
chat = model.start_chat()

class BotModel:
    def send_message(prompt, image=None, retry=3):
        
        """
        prompt : str
        image : PIL.Image=None
        retry : int = 3
        Send's a message using google.generativeai's with handling for multimodal inputs.
        Returns `GenerateContentResponse` (Will require .text)
        """
        if image:
            image_addon = "Describe this image to yourself and use it to answer any question the user asks"
            prompt = prompt + "\n" + image_addon + "\n"
            try:
                response = chat.send_message([prompt, image])
                return response.text
            except Exception as error:
                chat.rewind()
                print("BotModel.py: Error: ", error)
        try:
            response = chat.send_message(prompt)
            return response.text
        except Exception as error:
            chat.rewind()
            print("BotModel.py: Error: ", error)
            return "Sorry, could you say that again?"


# while True:
#     x = input("> ")
#     response = BotModel.send_message(prompt=x)
#     print(response)

# This file will be removed on version 0.7 alpha as it is no longer needed.