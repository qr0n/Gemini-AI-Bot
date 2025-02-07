"""
This is the API for discord interactions.
"""

import json
import os
from discord.ext import commands
from discord import Message
from modules.Memories import Memories
from modules.BotModel import read_prompt, BotModel, headless_BotModel
from modules.ManagedMessages import ManagedMessages, headless_ManagedMessages
from modules.AIAgent import AIAgent

context_window = ManagedMessages().context_window
memories = Memories()

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)


class Gemini:

    async def generate_response(message: Message, ctx: commands.Context):
        """Accepts discord.Message object and auto-handles everything"""

        message = ctx.message
        channel_id = (
            ctx.message.channel.id
        )  # declare channel id (channel id is unique for context window)
        message_id = ctx.message.id  # declare message id
        attachments = ctx.message.attachments  # declare message attachments

        if channel_id not in context_window:
            context_window[channel_id] = (
                []
            )  # if channel id isnt present in context window, make a new key

        message_in_list = await ManagedMessages.add_to_message_list(
            channel_id,
            message_id,
            f"{ctx.message.author.display_name}: {ctx.message.content}",
        )
        # appends the message to the context window, "user: message"
        # auto manages context window size

        remembered_memories = await memories.compare_memories(
            channel_id, message.content
        )

        if remembered_memories["is_similar"]:
            prompt = read_prompt(message, remembered_memories["similar_phrase"])
        else:
            prompt = read_prompt(message)

        if attachments and attachments[0].filename.lower().endswith(
            (
                ".png",
                ".jpg",
                ".webp",
                ".heic",
                ".heif",
                ".mp4",
                ".mpeg",
                ".mov",
                ".wmv",
            )
        ):
            # Checks if file type is one supported by Google Gemini
            save_name = str(message.id) + " " + message.attachments[0].filename.lower()
            await message.attachments[0].save(save_name)  # Saves attachment

            file = await BotModel.upload_attachment(save_name)
            response = await BotModel.generate_content(prompt, channel_id, file)

            # uploads using FileAPI

            await ManagedMessages.add_to_message_list(
                channel_id,
                message_id,
                f"{message.author.display_name}: {message.content}",
            )

            os.remove(save_name)
            await BotModel.delete_attachment(file)
            return response

        # Add text file and audio support soon
        elif attachments and attachments[0].filename.lower().endswith(
            (".wav", ".mp3", ".aiff", ".aac", ".flac")
        ):
            # Audio handling

            save_name = str(message.id) + " " + message.attachments[0].filename.lower()
            await message.attachments[0].save(save_name)
            # Download the file

            file = await BotModel.upload_attachment(save_name)
            response = await BotModel.generate_content(
                prompt=prompt, channel_id=channel_id, attachment=file
            )

            os.remove(save_name)
            await BotModel.delete_attachment(file)
            return response

        elif attachments and attachments[0].filename.lower().endswith(".ogg"):

            save_name = str(message.id) + " " + message.attachments[0].filename.lower()
            await message.attachments[0].save(save_name)
            file = await BotModel.upload_attachment(save_name)
            stt_response = await BotModel.speech_to_text(audio_file=file)

            # Remove initial message appended.
            await ManagedMessages.remove_from_message_list(channel_id, message_in_list)

            await ManagedMessages.add_to_message_list(
                channel_id, message_id, f"{message.author.display_name}: {stt_response}"
            )
            # Add message from Voice note to list

            response = await BotModel.generate_content(
                prompt=prompt, channel_id=channel_id
            )

            os.remove(save_name)
            await BotModel.delete_attachment(file)
            return response

        else:
            if config["AGENT"]["enabled"]:
                category = await AIAgent.classify(message.content)  # AGENT HOOK
                await AIAgent.categorize(category, ctx)  # AGENT HOOK

            response = await BotModel.generate_content(
                prompt, channel_id
            )  # DISCORDBOT.PY
            return response


class headless_Gemini:

    async def generate_response(channel_id, author_name, author_content):

        if channel_id not in context_window:
            context_window[channel_id] = (
                []
            )  # if channel id isnt present in context window, make a new key

        await headless_ManagedMessages.add_to_message_list(
            channel_id=channel_id, text=f"{author_name} : {author_content}"
        )

        remembered_memories = await memories.compare_memories(
            channel_id, author_content
        )

        if remembered_memories["is_similar"]:
            prompt = read_prompt(
                memory=remembered_memories["similar_phrase"], author_name=author_name
            )
        else:
            prompt = read_prompt(author_name=author_name)

        response = await headless_BotModel.generate_content(
            channel_id=channel_id, prompt=prompt
        )
        return response
