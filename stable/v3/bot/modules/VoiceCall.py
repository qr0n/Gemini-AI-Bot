"""
This is a file chunked from the original cogs/voice.py for modules/AIAgent.py
This file provides functions for the agent to work, and will probably help organize the code

TODO:
- Fix leave rejoin bug
- Fix double audio issue
"""

import discord
import asyncio
import json
import os
import io

from elevenlabs.client import ElevenLabs
from elevenlabs import stream
from discord.ext import commands
from discord import AllowedMentions
from typing import Dict
from modules.BotModel import BotModel
from modules.CommonCalls import CommonCalls


connections: Dict[int, discord.VoiceClient] = {}
client = ElevenLabs(api_key=CommonCalls.config()["elevenlabs_api_key"])
allowed_mentions = AllowedMentions(
    everyone=False, users=False, roles=False, replied_user=False
)


class VoiceCalls:

    async def say_with_elevenlabs(
        voice_client: discord.VoiceClient, text, voice="Antoni"
    ):
        # Generate audio
        _audio = client.generate(text=text, voice=voice, model="eleven_multilingual_v2")

        audio = stream(_audio)

        # Convert audio to a file-like object
        audio_file = io.BytesIO(audio)

        # Play the audio
        voice_client.play(discord.FFmpegPCMAudio(audio_file, pipe=True))

        # Wait until the audio finishes playing
        while voice_client.is_playing():
            await asyncio.sleep(1)

    async def once_done(
        sink: discord.sinks,
        channel: discord.TextChannel,
        voice_client: discord.VoiceClient,
        ctx: commands.Context,
    ):  # Our voice client already passes these in.

        from modules.DiscordBot import headless_Gemini

        for user_id, audio in sink.audio_data.items():
            file_name = f"./{user_id}.{sink.encoding}"
            author_name = ctx.message.author  # TODO: Change to bot.getch_member

            with open(file_name, "wb") as f:
                audio.file.seek(0)
                f.write(audio.file.read())
                f.close()

            file = await BotModel.upload_attachment(file_name)  # Uploads
            stt = await BotModel.speech_to_text(audio_file=file)  # Converts to text +1

            response = await headless_Gemini.generate_response(
                channel_id=channel.id, author_name=author_name, author_content=stt
            )

            await VoiceCalls.say_with_elevenlabs(
                voice_client=voice_client, text=response
            )

            os.remove(file_name)  # Deletes the recorded file
            await BotModel.delete_attachment(
                file.name
            )  # Deletes the recorded file off google

            # Only start a new recording if we're still connected
            if voice_client and voice_client.is_connected():
                vc = connections.get(ctx.guild.id)
                if vc and vc.is_connected():
                    vc.start_recording(
                        discord.sinks.WaveSink(), VoiceCalls.once_done, channel, vc, ctx
                    )
                    await asyncio.sleep(float(CommonCalls.config()["recording-time"]))
                    vc.stop_recording()

    async def start_recording(ctx: commands.Context) -> None:
        voice: discord.Member.voice = ctx.author.voice

        if not voice:
            await ctx.send("You aren't in a voice channel!")
            return

        # Check if we already have a connection for this guild
        if ctx.guild.id in connections and connections[ctx.guild.id].is_connected():
            vc = connections[ctx.guild.id]
        else:
            try:
                vc: discord.VoiceClient = await voice.channel.connect()
            except discord.ClientException:
                await ctx.send(
                    "I couldn't connect to the voice channel. Please check my permissions."
                )
                return
            connections[ctx.guild.id] = vc

        print(connections)

        vc.start_recording(
            discord.sinks.WaveSink(), VoiceCalls.once_done, ctx.channel, vc, ctx
        )

        await ctx.send("Listening!")

        await asyncio.sleep(float(CommonCalls.config()["recording-time"]))

        vc.stop_recording()

    async def stop_recording(ctx: commands.Context) -> None:
        """
        Description:
        This function gracefully ends the voice call session by disconnecting from the voice channel and stopping future records

        Arguments:
        ctx : commands.Context

        Returns:
        None
        """

    # TODO Add this lol
