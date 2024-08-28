"""
This module is a WIP for Deep Context development and testing
TODO : 
- overhaul AIAgent.py
- apply patch to DiscordBot.py
"""

import google.generativeai as genai
import json
import datetime

from discord.ext import commands
from google.generativeai.types import HarmCategory
from modules.ManagedMessages import ManagedMessages
from modules.VoiceCall import VoiceCalls
from modules.agent.reminder import Reminder
from modules.CommonCalls import CommonCalls

class DeepContext:
    """
    Parent class hosting both DeepContext Logic and DeepContext Hook
    """

    class Logic:

        async def classify(text : str, author_name : str, server_id : int = None, channel_id : int = None):
            """
            Description -
            This function uses the Google Gemini API to classify text input from discord, based on the message it categorizes it into events.
            
            Arguments - 
            `text : str`
        
            Returns - 
            `clean_json : dict`
            """

            json_format = """{"category" : general-category-type, "hidden-meaning" : the hidden meaning of the text}"""
            remind_json = """{"category" : general-category-type, "datetime" : yyyy-mm-dd hh:mm:ss, "reason" : the reason why the reminder is made}"""
            system_instruction = f"""
            You are an AI Agent named "{CommonCalls.load_character_details()['name']}"\n
            however you will avoid referring to yourself as an AI or LLM,\n
            The person who's data you're classifying is named {author_name}\n
            ONLY initialize events when the user is mentioning YOUR name.\n
            
            you have two primary objectives, you will compile the evaluated and return as one.\n
            Your first objective is to classify the following chunk of text into one of the following action categories\n
            make sure to analyze this very carefully and answer carefully.\n
            
            voice-call-initialize : When the user would like initialize a voice call with the user (keywords like call, speak and talk)\n
            voice-call-end : When the user would like to end a voice call with the user (keywords like later, nice speaking and bye)\n

            normal-chat-normal: When theres nothing interesting occuring in the current chat, just regular conversation\n
            interesting-chat-good : When the conversation is dicussing something that falls within the likes {CommonCalls.load_character_details()["likes"]}\n
            interesting-chat-bad  : When the conversation is discussing something that falls within the dislikes {CommonCalls.load_character_details()["dislikes"]}\n

            reminder-start : When the message is asking you to set a reminder the current date time is {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")},\n
            modify the returned JSON as such {remind_json} (keywords like "remind me")\n
            reminder-cancel : When the message is asking you to cancel a reminder. (keywords like "cancel reminder")\n

            Your second objective is to find any hidden meanings in the text, any implied actions, \n
            meanings or otherwise identify at least 3 (three) of these, if there is none, \n\n
            
            Return the classified text in the following json format:\n
            {json_format}
            """
            agent_model = genai.GenerativeModel(CommonCalls.config()["GEMINI"]["AI_MODEL"],
                                                system_instruction=system_instruction, 
                                                generation_config={"response_mime_type": "application/json"}, 
                                                safety_settings={
                                                HarmCategory.HARM_CATEGORY_HARASSMENT : CommonCalls.config()["GEMINI"]["FILTERS"]["sexually_explicit"],
                                                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT : CommonCalls.config()["GEMINI"]["FILTERS"]["harassment"],
                                                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT : CommonCalls.config()["GEMINI"]["FILTERS"]["dangerous_content"],
                                                HarmCategory.HARM_CATEGORY_HATE_SPEECH : CommonCalls.config()["GEMINI"]["FILTERS"]["hate_speech"]})

            response = await agent_model.generate_content_async(text)
            if CommonCalls.clean_json(response.text.lower())["category"] in ["voice-call-initialize", "voice-call-end", "normal-chat-normal", "interesting-chat-good", "interesting-chat-bad", "none-none"]:
                # Checks if the json keys are valid
                return CommonCalls.clean_json(response.text)

            else:
                return CommonCalls.clean_json(response.text)
            
        def modifier(input_json : dict):
            """
            Description -
            Takes input from DeepContext.Logic.classify,
            checks if event called is an event that needs text generation
            if so, add flag `kill`
    
            Arguments -
            input_json type : `dict`

            Returns -
            modified_json type : `dict`
            """

            watch_list = ["voice-call-initialize"]
            if input_json["category"] in watch_list:
                input_json["kill"] = True
                return input_json
            
            else:
                return input_json
            

    #     async def event_caller(event : dict, ctx : commands.Context):

    #         match event["category"]:

    #             case "voice-call-initialize":
                    
    #                 print("Voice call event fired")
            
    #             case "voice-call-end":
    #                 await VoiceCalls.stop_recording(ctx)
            
    #             case "reminder-start":                               # START EXAMPLE
    #                 reminder_reason = ai_function.get("reason")
    #                 reminder_date = ai_function.get("datetime", None)
    #                 reminder_channel = ctx.channel.id
    #                 reminder_message_author = ctx.author.id
    #                 await Reminder.add_reminder(reminder_name=reminder_reason,
    #                                             reminder_time=reminder_date, 
    #                                             reminder_channel_id=reminder_channel,
    #                                             reminder_message_author=reminder_message_author)
    #                                                                 # END EXAMPLE 
    #             case _:

    # class Hook:


            