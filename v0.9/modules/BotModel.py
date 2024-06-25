import google.generativeai as genai
import json
import re
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
    async def generate_content(prompt, channel_id=None, attachment=None, retry=3):
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
            image_addon = "Describe this piece of media to yourself in a way that if referenced again, you will be able to answer any potential question asked."
            # full_prompt = [_prompt, "\n", image_addon, "\n", attachment] # Old stuff, experimenting with google file api
            # attachment_file = genai.upload_file(attachment)
            full_prompt = [_prompt, "\n", attachment]
        else:
            full_prompt = [_prompt]

        response = await model.generate_content_async(full_prompt)

        try:
            text = response.text.strip()
            context_window[channel_id].append(f"{character_name}: {text}")
            
            return text
        except Exception as error:
            if attachment:
                print(attachment)
                print(type(attachment))
                # genai.delete_file(attachment) # Ensure the file gets deleted 

            print("BotModel.py: Error: While generating a response, this exception occurred", error)
    
        retry_count = 0
        while retry_count < retry:
            try: 
                fall_back_response = response.candidates[0].content.parts
                context_window[channel_id].append(f"{character_name}: {str(fall_back_response).strip()}")
                return str(fall_back_response).strip()
            except Exception as E:
                print(f"Error generating response (retry {retry_count}): {E}")
                retry_count += 1

        try:
            context_window[channel_id].pop(0)
        except (IndexError, KeyError):
            pass
        return config["MESSAGES"]["error"] or "Sorry, could you please repeat that?"
    
    # async def generate_reaction(prompt, channel_id, attachment=None):
    #     reaction_model = genai.GenerativeModel(model_name=config["GEMINI"]["AI_MODEL"], system_instruction=prompt)

    #     if attachment:
    #         prompt_with_image = ["\n".join(context_window[channel_id]), attachment]
    #         emoji = await reaction_model.generate_content_async(prompt_with_image)
            
    #         response = emoji.text or emoji.candidates[0]
    #         #context_window[channel_id].append(f"You reacted with this emoji {response}")
            
    #         return response
        
    #     else:
    #         context = '\n'.join(context_window[channel_id])
    #         emoji = reaction_model.generate_content(context)
            
    #         response = emoji.text or emoji.candidates[0]
    #         #context_window[channel_id].append(f"You reacted with this emoji {response}")
    #         return response
        