import discord
from discord.ext import commands
import asyncio
import speech_recognition as sr
from typing import Dict, Any
import io


async def once_done(sink: discord.sinks.WaveSink, channel: discord.TextChannel, *args: Any) -> None:
    recorded_users = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items()]
    await sink.vc.disconnect()

    files = [discord.File(audio.file, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]
    await channel.send(f"Finished recording audio for: {', '.join(recorded_users)}.", files=files)

    # Transcription logic
    recognizer = sr.Recognizer()
    for user_id, audio in sink.audio_data.items():
        try:
            # Convert BytesIO to AudioFile
            with io.BytesIO(audio.file.getvalue()) as audio_file:
                with sr.AudioFile(audio_file) as source:
                    audio_data = recognizer.record(source)
            
            # Use asyncio.to_thread for potentially blocking operations
            text = await asyncio.to_thread(recognizer.recognize_tensorflow, audio_data)
            await channel.send(f"Transcription for <@{user_id}>: {text}")
        except sr.UnknownValueError:
            await channel.send(f"Couldn't understand the audio for <@{user_id}>.")
        except sr.RequestError as e:
            await channel.send(f"Error requesting results from Google Speech Recognition service for <@{user_id}>: {e}")

connections: Dict[int, discord.VoiceClient] = {}

class TranscriptionCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.command()
    async def start_recording(self, ctx: commands.Context) -> None:
        voice = ctx.author.voice
        if not voice:
            await ctx.send("You aren't in a voice channel!")
            return

        try:
            vc = await voice.channel.connect()
        except discord.ClientException:
            await ctx.send("I couldn't connect to the voice channel. Please check my permissions.")
            return

        connections[ctx.guild.id] = vc

        vc.start_recording(
            discord.sinks.WaveSink(),
            once_done,
            ctx.channel
        )

        await ctx.send("Started recording!")

    @commands.command()
    async def stop_recording(self, ctx: commands.Context) -> None:
        if ctx.guild.id in connections:
            vc = connections[ctx.guild.id]
            vc.stop_recording()
            del connections[ctx.guild.id]
            await ctx.message.delete()
        else:
            await ctx.send("I am currently not recording here.")

def setup(bot: commands.Bot) -> None:
    bot.add_cog(TranscriptionCog(bot))