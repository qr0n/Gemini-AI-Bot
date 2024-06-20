# TODO add multimodal support.
import google.generativeai as genai
import json
# from modules.Memories import Memories
from modules.ContextWindow import ContextWindow # TODO Implement context window
from discord import Message
from PIL import Image

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

# context_window = ContextWindow() # TODO : Reimplement ContextWindow
context_window = ContextWindow().context_window

genai.configure(api_key=config["GEMINI"]["API_KEY"])

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

def read_prompt(message: Message = None, memory=None):
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

        author_name = message.author.name if message else "unknown_user"
        bot_name = load_character_details()['name'] 

        # If memory is present, append to the prompt | TODO : append to prompt for context window
        if memory: 
            return f"""
        {system_note}

        You are {name}, a {role}, who is {age} years old, described as {description}.
        People in conversation {bot_name} (you), {author_name}, your job is to respond to the last message of {author_name}.
        You can use the messages in your context window, but do not ever reference them.

        Conversation examples:

        {"\n".join([f"{author_name}: {example['user']}\n{bot_name}: {example['bot']}" for example in conversation_examples])}

        Currently relevnt memories:

        {memory}
        
        From here on out, this is the conversation you will be responding to.
        ---- CONVERSATION ----
""" 

        # If not
        return f"""
        {system_note}

        You are {name}, a {role}, who is {age} years old, described as {description}.
        People in conversation {bot_name} (you), {author_name}, your job is to respond to the last message of {author_name}.
        You can use the messages in your context window, but do not ever reference them.

        Conversation examples:

        {"\n".join([f"{author_name}: {example['user']}\n{bot_name}: {example['bot']}" for example in conversation_examples])}
        
        From here on out, this is the conversation you will be responding to.
        ---- CONVERSATION ----
        """

model = genai.GenerativeModel(config["GEMINI"]["AI_MODEL"], system_instruction=read_prompt(), safety_settings={})

class BotModel:
    # Generate content
    def generate_content(prompt, channel_id=None, attachment=None, retry=3):
        """
        prompt: str
        channel_id : str (guild-user)
        attachment : Image (PIL) = None
        retry : int = 3
        Assumes if attachment is present, it will be appended to the context window from cog
        """
        character_name = load_character_details()['name']
        context = '\n'.join(context_window[channel_id])
        _prompt = prompt + "\n" + context
        if attachment:
            image_addon = "Describe this peice of media to yourself in a way that if referenced again, you will be able to answer any potential question asked."
            full_prompt = [_prompt, "\n", image_addon, "\n", attachment]
            try:
                response = model.generate_content(full_prompt).text
                context_window[channel_id].append(f"{character_name}: {response.strip()}")
                return response
            except Exception as error:
                print("BotModel.py: Error: While generating a response, this exception occured", error)
                retry_count = 0
                while retry_count < retry:
                    response = model.generate_content(full_prompt).candidates
                    return response[0]
                else:
                    try:
                        context_window[channel_id].pop(0)
                    except IndexError or KeyError:
                        pass
                    return "Sorry, could you please repeat that?"
        try:
            response = model.generate_content(_prompt).text
            # Strip bot's name from the response
            response = response[len(f"{character_name}: "):] if response.startswith(f"{character_name}: ") else response
            context_window[channel_id].append(f"{character_name}: {response.strip()}")
            return response
        except Exception as error:
            print(f"Botmodel.py: Error: generating response: {error}")
            retry_count = 0
            while retry_count < retry:  # Adjust the retry count as needed
                try:
                    response_goog = model.generate_content(full_prompt)
                    response = response_goog.candidates[0]
                    # Strip bot's name from the response
                    response = response[len(f"{character_name}: "):] if response.startswith(f"{character_name}: ") else response
                    context_window[channel_id].append(f"{character_name}: {response.strip()}")
                    return response
                except Exception as E:
                    print(f"Error generating response (retry {retry_count}): {E}")
                    retry_count += 1
            else:
                try:
                    context_window[channel_id].pop(0)
                except KeyError or IndexError:
                    pass
                return "Sorry, could you please repeat that?"