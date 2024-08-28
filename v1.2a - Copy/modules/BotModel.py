import json
import asyncio
import google.generativeai as genai

from modules.ManagedMessages import ManagedMessages, headless_ManagedMessages
from discord import Message
from google.generativeai.types import HarmCategory, HarmBlockThreshold

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

context_window = ManagedMessages().context_window

genai.configure(api_key=config["GEMINI"]["API_KEY"])

def load_character_details():
    """
    Description:
    Handles the `prompt.json` and returns the personality details.

    Arguments:
    None

    Returns:
    Dict[str, str]
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
    likes = personality_traits.get('likes', "N/A")
    dislikes = personality_traits.get("dislikes", "N/A")

    return {
        "name": name,
        "role": role,
        "age": age,
        "description": description,
        "likes" : likes,
        "dislikes" : dislikes
    }

def read_prompt(message: Message = None, memory: str = None, author_name: str = None):
        """
        Description:
        This function reads the prompt from `prompt.json` and formats the values correctly

        Arguments:
        message : discord.Message = None
        memory : str = None
        author_name : str = None
 
        Returns:
        prompt : str | prompt_with_memory : str
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
        likes = personality_traits.get('likes', "N/A")
        dislikes = personality_traits.get("dislikes", "N/A")

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

        Your likes : {likes}
        
        Your dislikes: {dislikes}

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
        
        Your likes : {likes}
        
        Your dislikes: {dislikes}
        
        Conversation examples:

        {"\n".join([f"{author_name}: {example['user']}\n{bot_name}: {example['bot']}" for example in conversation_examples])}

        From here on out, this is the conversation you will be responding to.
        ---- CONVERSATION ----
        """

model = genai.GenerativeModel(config["GEMINI"]["AI_MODEL"], system_instruction=read_prompt(), safety_settings={})

class BotModel:
    """
    This class deals with how the discord bot generates text and gets different inputs
    NOTE: This class NEEDS discord objects for use-cases without an object use `headless_BotModel`
    """
    # Generate content
    async def generate_content(prompt, channel_id=None, attachment : genai.types.File = None, retry=3):
        """
        Description: 
        This function handles asynchronos text generation using Gemini, this also allows for multimodal prompts using a pre-uploaded file

        Arguments:
        prompt : str
        channel_id : int | str = None
        attachment : genai.types.File = None
        retry : int = 3

        Returns:
        response : str
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
                fall_back_response = response.candidates[0].content.parts[0].text
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
        """
        Description:
        This function allows for asynchronous attachment uploading via FileAPI

        Arguments:
        attachment
        
        Returns:
        attachment_media : genai.Types.File | None
        """
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
            
    async def delete_attachment(attachment):
        """
        come on, really?
        """
        genai.delete_file(attachment)

    async def __generate_reaction(prompt, channel_id, attachment=None):
        """[UNUSED AND BUGGY]"""
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
        Description:
        This function is used for transcription of audio data provided via voice channels or .ogg files
        
        Arguments:
        audio_file : genai.Types.File

        Returns:
        response.text : str
        """
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
        [UNUSED AND BUGGY]
        """

        system_instruction = """You are 'Sponge' in this conversation. You now have the ability to send one emoji, """
        reaction_model = genai.GenerativeModel(model_name=config["GEMINI"]["AI_MODEL"], system_instruction=prompt)

class headless_BotModel:
    """
    This class deals use cases that do not provide a discord object (somewhat)"""

    async def generate_content(channel_id : str | int, prompt : str, retry : int =3):
        """
        Description:
        This function generates text content
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