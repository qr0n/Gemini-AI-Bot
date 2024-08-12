import json
import asyncio
import google.generativeai as genai
import speech_recognition as sr
from modules.ManagedMessages import ManagedMessages, headless_ManagedMessages
from discord import Message
from google.generativeai.types import HarmCategory, HarmBlockThreshold

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

context_window = ManagedMessages().context_window

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

def read_prompt(message: Message = None, memory=None, author_name=None):
        """This function reads the prompt inside prompt.json and formats in a usable system instruction
        message : discord.Message
        memory = None
        """
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

        author_name = message.author.name if message else author_name or "unknown_user" 
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

        Context information is below.
        ---------------------
        {memory}
        ---------------------
        Given the context information and not prior knowledge answer using THIS information

        
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
    async def generate_content(prompt, channel_id=None, attachment : genai.types.File = None, retry=3):
        """
        This is the function responsible for asynchronous text generation using Gemini 
        prompt : Any*,
        channel_id : int,
        attachment : genai.types.File = None,
        retry = 3
        """
        
        context = '\n'.join(context_window[channel_id])
        prompt_with_context = prompt + "\n" + context

        if attachment:
            media_addon = "Describe this piece of media to yourself in a way that if referenced again, you will be able to answer any potential question asked."
            # full_prompt = [_prompt, "\n", image_addon, "\n", attachment] # Old stuff, experimenting with google file api
            # attachment_file = genai.upload_file(attachment)
            full_prompt = [prompt_with_context, "\n", media_addon , "\n", attachment]

        else:
            full_prompt = prompt_with_context

        response = await model.generate_content_async(full_prompt, safety_settings={
                                                        HarmCategory.HARM_CATEGORY_HARASSMENT : config["GEMINI"]["FILTERS"]["sexually_explicit"],
                                                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT : config["GEMINI"]["FILTERS"]["harassment"],
                                                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT : config["GEMINI"]["FILTERS"]["dangerous_content"],
                                                        HarmCategory.HARM_CATEGORY_HATE_SPEECH : config["GEMINI"]["FILTERS"]["hate_speech"]
                                                        })

        try:
            text = response.text.strip()
            return text
        
        except Exception as error:
            print("BotModel.py: Error: While generating a response, this exception occurred", error)
            print(response.candidates)
    
        retry_count = 0
        while retry_count < retry:
            try: 
                fall_back_response = response.candidates[0].content.parts
                return str(fall_back_response).strip()
            except Exception as E:
                print(f"Error generating response (retry {retry_count}): {E}")
                retry_count += 1

        try:
            await ManagedMessages.remove_message_from_index(channel_id, 0)
        except (IndexError, KeyError):
            pass
        return config["MESSAGES"]["error"] or "Sorry, could you please repeat that?"
    
    async def upload_attachment(attachment):
        print("[INIT] Uploading Attachment function call `BotModel.upload_attachment` (Message from line 168 @ modules/BotModel.py)")
        attachment_media = genai.upload_file(attachment)
    
        while True:
            if attachment_media.state.name == "PROCESSING":
                print("[PROCESSING] Uploading Attachment function call `BotModel.upload_attachment` (Message from line 173 @ modules/BotModel.py)")
                await asyncio.sleep(2)
                attachment_media = genai.get_file(attachment_media.name)  # Update the state
            elif attachment_media.state.name == "ACTIVE":
                print("[SUCCESS] Uploading Attachment function call `BotModel.upload_attachment` (Message from line 177 @ modules/BotModel.py)")
                return attachment_media
            elif attachment_media.state.name == "FAILED":
                print("[FAILED] Uploading Attachment function call `BotModel.upload_attachment` (Message from line 180 @ modules/BotModel.py)")
                return None
            else:
                print(f"Unknown state: {attachment_media.state.name}")
                return None
    
    async def __generate_reaction(prompt, channel_id, attachment=None):
        reaction_model = genai.GenerativeModel(model_name=config["GEMINI"]["AI_MODEL"], system_instruction=prompt)

        if attachment:
            prompt_with_image = ["\n".join(context_window[channel_id]), attachment]
            emoji = await reaction_model.generate_content_async(prompt_with_image)
            
            response = emoji.text or emoji.candidates[0]
            #context_window[channel_id].append(f"You reacted with this emoji {response}")
            
            return response
        
        else:
            context = '\n'.join(context_window[channel_id])
            emoji = reaction_model.generate_content(context)
            
            response = emoji.text or emoji.candidates[0]
            #context_window[channel_id].append(f"You reacted with this emoji {response}")
            return response
        
    async def speech_to_text(audio_file : genai.types.File):
        """
        [async]
        This function is called when a `.ogg` file is uploaded to discord"""
        print("Speech To Text function call `speech_to_text` (Message from line 210 @ modules/BotModel.py)")
        system_instruction = """You are now a microphone, you will ONLY return the words in the audio file, DO NOT describe them."""
        speech_to_text_model = genai.GenerativeModel(config["GEMINI"]["AI_MODEL"], system_instruction=system_instruction, safety_settings={
                                                    HarmCategory.HARM_CATEGORY_HARASSMENT : config["GEMINI"]["FILTERS"]["sexually_explicit"],
                                                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT : config["GEMINI"]["FILTERS"]["harassment"],
                                                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT : config["GEMINI"]["FILTERS"]["dangerous_content"],
                                                    HarmCategory.HARM_CATEGORY_HATE_SPEECH : config["GEMINI"]["FILTERS"]["hate_speech"]
                                                    })
        
        response = await speech_to_text_model.generate_content_async(["describe this audio file\n", audio_file])
        print("[RESPONSE] Response from STT Module: ", response.text)
        return response.text       
    
    async def generate_reaction(prompt, channel_id : str | int, attachment : genai.types.File=None):
        """
        This function generates an emotion that is then represented by an emoji and reacted with by the bot
        
        prompt: Any
        channel_id : str or int
        attachment : genai.types.File = None

        returns `something lol`
        """

        system_instruction = """You are 'Sponge' in this conversation. You now have the ability to send one emoji, """
        reaction_model = genai.GenerativeModel(model_name=config["GEMINI"]["AI_MODEL"], system_instruction=prompt)

class headless_BotModel:

    async def generate_content(channel_id : str | int, prompt : str, retry : int =3):
        """
        Accepts channel_id : str or int
        prompt : str 
        retry : int = 3
        """

        headless_mm = headless_ManagedMessages
        
        context = '\n'.join(headless_mm.context_window[channel_id])
        full_prompt = prompt + "\n" + context
        # TODO HERE REMOVE THIS AND OPTIMIZE BY SENDING VOICE MESSAGE DIRECTLY TO API
        response = await model.generate_content_async(full_prompt, safety_settings={
                                                        HarmCategory.HARM_CATEGORY_HARASSMENT : config["GEMINI"]["FILTERS"]["sexually_explicit"],
                                                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT : config["GEMINI"]["FILTERS"]["harassment"],
                                                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT : config["GEMINI"]["FILTERS"]["dangerous_content"],
                                                        HarmCategory.HARM_CATEGORY_HATE_SPEECH : config["GEMINI"]["FILTERS"]["hate_speech"]
                                                        })
        
        try:
            text = response.text.strip()
            return text
        
        except Exception as error:
            print("[headless_BotModel] BotModel.py: Error: While generating a response, this exception occurred", error)
            print(response.candidates)
    
        retry_count = 0
        while retry_count < retry:
            try: 
                fall_back_response = response.candidates[0].content.parts
                return str(fall_back_response).strip()
            except Exception as E:
                print(f"Error generating response (retry {retry_count}): {E}")
                retry_count += 1

        try:
            await headless_ManagedMessages.remove_message_from_index(channel_id, 0)

        except (IndexError, KeyError):
            pass

        return config["MESSAGES"]["error"] or "Sorry, could you please repeat that?"
    
        
