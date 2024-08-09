"""
This is the API for discord interactions.
"""

import json
import os
from discord import Message
from modules.Memories import Memories
from modules.BotModel import read_prompt, BotModel
from modules.ManagedMessages import ManagedMessages

context_window = ManagedMessages().context_window
memories = Memories()

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

class Gemini:

    async def generate_response(message : Message):
        """Accepts discord.Message object and auto-handles everything"""
        
        channel_id = message.channel.id # declare channel id (channel id is unique for context window)
        message_id = message.id # declare message id
        attachments = message.attachments # declare message attachments

        if channel_id not in context_window:
            context_window[channel_id] = [] # if channel id isnt present in context window, make a new key
            
        message_in_list = await ManagedMessages.add_to_message_list(channel_id, message_id, f"{message.author.display_name}: {message.content}")
        # appends the message to the context window, "user: message"
        # auto manages context window size

        remembered_memories = await memories.compare_memories(channel_id, message.content)
        
        if remembered_memories["is_similar"]:
            prompt = read_prompt(message, remembered_memories["similar_phrase"])
        else: 
            prompt = read_prompt(message)

        if attachments and attachments[0].filename.lower().endswith((".png", ".jpg", ".webp", ".heic", ".heif", ".mp4", ".mpeg", ".mov", ".wmv",)):
            # Checks if file type is one supported by Google Gemini
            save_name = str(message.id) + " " + message.attachments[0].filename.lower()
            await message.attachments[0].save(save_name) # Saves attachment
            
            file = await BotModel.upload_attachment(save_name)
            response = await BotModel.generate_content(prompt, channel_id, file)

            # uploads using FileAPI
            
            await ManagedMessages.add_to_message_list(channel_id, message_id, f"{message.author.display_name}: {message.content}")

            os.remove(save_name)
            return response
        
        # Add text file and audio support soon
        elif attachments and attachments[0].filename.lower().endswith((".wav", ".mp3", ".aiff", ".aac", ".flac")):
            # Audio handling

            save_name = str(message.id) + " " + message.attachments[0].filename.lower()
            await message.attachments[0].save(save_name)
            # Download the file

            file = await BotModel.upload_attachment(save_name)
            response = await BotModel.generate_content(prompt=prompt, channel_id=channel_id, attachment=file)
            
            return response
        
        elif attachments and attachments[0].filename.lower().endswith(".ogg"):

            save_name = str(message.id) + " " + message.attachments[0].filename.lower()
            await message.attachments[0].save(save_name)
            file = await BotModel.upload_attachment(save_name)
            response = await BotModel.speech_to_text(audio_file=file)

            # Remove initial message appended.
            await ManagedMessages.remove_from_message_list(channel_id, message_in_list)
            
            await ManagedMessages.add_to_message_list(channel_id, message_id, f"{message.author.display_name}: {response}")
            # Add message from Voicenote to list

        else:
            response = await BotModel.generate_content(prompt, channel_id)
            return response