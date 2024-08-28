"""
This is a file chunked from the original cogs/voice.py for modules/AIAgent.py
This file provides functions for the agent to work, and will probably help organize the code
"""

import discord
import asyncio
import json
import os
import io

from elevenlabs.client import ElevenLabs
from elevenlabs import play, stream, save
from discord.ext import commands, tasks
from discord import AllowedMentions
from typing import Dict
from modules.BotModel import BotModel

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

connections: Dict[int, discord.VoiceClient] = {}
client = ElevenLabs(api_key=config["VOICE"]["elevenlabs_api_key"])
allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False, replied_user=False)

class VoiceCalls:

    async def say_with_elevenlabs(voice_client : discord.VoiceClient, text, voice="Antoni"):
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

        await voice_client.disconnect()

    async def once_done(sink: discord.sinks, channel: discord.TextChannel, voice_client : discord.VoiceClient, ctx : commands.Context):  # Our voice client already passes these in.
        
        from modules.DiscordBot import headless_Gemini

        #voice_client.stop_recording()  # Disconnect from the voice channel.
        author_name = ctx.message.author.name

        for user_id, audio in sink.audio_data.items():
            file_name = f'./{user_id}.{sink.encoding}'

            with open(file_name, 'wb') as f:
                audio.file.seek(0)
                f.write(audio.file.read())
                f.close()

            file = await BotModel.upload_attachment(file_name) # Uploads
            stt = await BotModel.speech_to_text(audio_file=file) # Converts to text +1 

            text = await channel.send(f"What I got:\n```{author_name} : {stt}```", allowed_mentions=allowed_mentions)

            response = await headless_Gemini.generate_response(channel_id=channel.id, author_name=author_name, author_content=stt) # Responds to converted + 1
            await text.reply(response)

            await VoiceCalls.say_with_elevenlabs(voice_client=voice_client, text=response)
            
            os.remove(file_name) # Deletes the recorded file
            await BotModel.delete_attachment(file) # Deletes the recorded file off google

            await VoiceCalls.start_recording(ctx)

        #await channel.send(f"Finished recording audio for: {', '.join(recorded_users)}.", file=discord.File(f"{user_id}.{sink.encoding}"))

    async def start_recording(ctx: commands.Context) -> None:
        voice = ctx.author.voice

        if not voice:
            await ctx.send("You aren't in a voice channel!")
            return

        try:
            vc : discord.VoiceClient = await voice.channel.connect()
        except discord.ClientException:
            await ctx.send("I couldn't connect to the voice channel. Please check my permissions.")
            return

        connections[ctx.guild.id] = vc

        vc.start_recording(
            discord.sinks.WaveSink(),
            VoiceCalls.once_done,
            ctx.channel,
            vc,
            ctx
        )
        
        await ctx.send("Listening!")

        await asyncio.sleep(config["VOICE"]["record_time"])

        vc.stop_recording()
        
        await ctx.send("Hold on! Let me process... :thinking:")

    async def stop_recording(ctx : commands.Context) -> None:
        """
        Description:
        This function gracefully ends the voice call session by disconnecting from the voice channel and stopping future records
        
        Arguments:
        ctx : commands.Context
        
        Returns:
        None
        """

    # TODO Add this lol