import json
import asyncio
import discord
import io, os

from discord.ext import commands
from modules.BotModel import BotModel
from modules.DiscordBot import headless_Gemini
from elevenlabs.client import AsyncElevenLabs
from elevenlabs import play, stream, save

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

client = AsyncElevenLabs(api_key=config["VOICE"]["elevenlabs_api_key"])
connections = {}

class VoiceChannel:

    async def say_with_elevenlabs(self, voice_client : discord.VoiceClient, text, voice="Antoni"):
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

        # Disconnect from the voice channel
        await voice_client.disconnect()

    async def start_recording(ctx : commands.Context):
        voice = ctx.author.voice

        if not voice:
            await ctx.send("You aren't in a voice channel!")
            return

        try:
            vc : discord.VoiceClient = await voice.channel.connect()
        except discord.ClientException:
            await ctx.send("I couldn't connect to the voice channel. Please check my permissions.")
            return
        
