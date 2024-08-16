"""
Refer to 
https://canary.discord.com/channels/1236174987325472768/1253245289733554185/1272413409400328292
https://cdn.discordapp.com/attachments/1252147217930649610/1272412754786910268/image.png?ex=66bae239&is=66b990b9&hm=e68868dfde1c5fc20548bf8c7f1c3aa1228ee4f18749520c73a5d5c4cc076eec&

For instructions 
To: Future Iron
"""

import google.generativeai as genai
import json
import datetime

from discord.ext import commands
from google.generativeai.types import HarmCategory
from modules.ManagedMessages import ManagedMessages
from modules.VoiceCall import VoiceCalls
from modules.agent.reminder import Reminder

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

context_window = ManagedMessages.context_window

genai.configure(api_key=config["GEMINI"]["API_KEY"])
model = genai.GenerativeModel(config["GEMINI"]["AI_MODEL"])

class AIAgent:

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

    def clean_json(nasty_json : str):
        """
        Description:
        This function cleans the potentially dirty json by removing the markdown
        
        Arguments:
        nasty_json : str
        
        Returns:
        nasty_json : dict
        """
        if nasty_json.startswith("```json") and nasty_json.endswith("```"):
            return json.loads(nasty_json[7:-3])
        else:
            return json.loads(nasty_json) # Assumed to be clean.. lol

    async def classify(text):
        """
        Description:
        This function uses the Google Gemini API to classify text input from discord, based on the message it categorizes it into events.
        
        Arguments:
        text : str
        
        Returns:
        clean_json : dict
        """
        json_format = """{"category" : general-category-type}"""
        remind_json = """{"category" : general-category-type, "datetime" : yyyy-mm-dd hh:mm:ss, "reason" : the reason why the reminder is made}"""
        system_instruction = f"""
        You are an AI Agent, your first task is classifying the following chunk of text into one of the following action categories
        make sure to analyze this very carefully and answer carefully.
        
        voice-call-initialize : When the user would like initialize a voice call with the user (keywords like call, speak and talk)
        voice-call-end : When the user would like to end a voice call with the user (keywords like later, nice speaking and bye)

        normal-chat-normal: When theres nothing interesting occuring in the current chat, just regular conversation
        interesting-chat-good : When the conversation is dicussing something that falls within the likes {AIAgent.load_character_details()["likes"]}
        interesting-chat-bad  : When the conversation is discussing something that falls within the dislikes {AIAgent.load_character_details()["dislikes"]}

        reminder-start : When the message is asking you to set a reminder the current date time is {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}, modify the returned JSON as such {remind_json} (keywords like "remind me")
        reminder-cancel : When the message is asking you to cancel a reminder. (keywords like "cancel reminder")

        Return the classified text in the following json format:
        {json_format}
        """
        
        agent_model = genai.GenerativeModel(config["GEMINI"]["AI_MODEL"], system_instruction=system_instruction, generation_config={"response_mime_type": "application/json"}, safety_settings={
                                                        HarmCategory.HARM_CATEGORY_HARASSMENT : config["GEMINI"]["FILTERS"]["sexually_explicit"],
                                                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT : config["GEMINI"]["FILTERS"]["harassment"],
                                                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT : config["GEMINI"]["FILTERS"]["dangerous_content"],
                                                        HarmCategory.HARM_CATEGORY_HATE_SPEECH : config["GEMINI"]["FILTERS"]["hate_speech"]})

        response = await agent_model.generate_content_async(text)
        if AIAgent.clean_json(response.text.lower())["category"] in ["voice-call-initialize", "voice-call-end", "normal-chat-normal", "interesting-chat-good", "interesting-chat-bad", "none-none"]:
            # Checks if the json keys are valid
            return AIAgent.clean_json(response.text)
        
        else:
            return AIAgent.clean_json(response.text)
        
    async def categorize(ai_function : dict, ctx : commands.Context):
        """
        Description:
        This function maps out the events with their functions.\n
        Depending on the function name this function will also append additional arguments

        Args:
        ai_function : str 
        ctx : commands.Context

        Returns:
        N/A
        """
        try:
            print(type(ai_function), ai_function)
            category = ai_function['category']
            match category:

                case "voice-call-initialize":
                    await VoiceCalls.start_recording(ctx)
                    return {"kill" : 1, "reason" : category} # for future logging
            
                case "voice-call-end":
                    await VoiceCalls.stop_recording(ctx)
            
                case "reminder-start":
                    reminder_reason = ai_function.get("reason")
                    reminder_date = ai_function.get("datetime", None)
                    reminder_channel = ctx.channel.id
                    reminder_message_author = ctx.author.id
                    await Reminder.add_reminder(reminder_name=reminder_reason,
                                                reminder_time=reminder_date, 
                                                reminder_channel_id=reminder_channel,
                                                reminder_message_author=reminder_message_author)
                    


                case _:
                    print(ai_function)

        except KeyError:
            return print("BAD")
