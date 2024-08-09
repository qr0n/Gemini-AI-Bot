import discord
from discord.ext import commands
import asyncio
import speech_recognition as sr
from typing import Dict, Any
import io

async def once_done(sink: discord.sinks, channel: discord.TextChannel, *args, ):  # Our voice client already passes these in.
    recorded_users = [  # A list of recorded users
        f"<@{user_id}>"
        for user_id, audio in sink.audio_data.items()]
    
    await sink.vc.disconnect()  # Disconnect from the voice channel.
    for user_id, audio in sink.audio_data.items():
        print(type(audio.file.read()))
        with open(f'./{user_id}.{sink.encoding}', 'wb') as f:
            audio.file.seek(0)
            f.write(audio.file.read())
        await channel.send(f"Finished recording audio for: {', '.join(recorded_users)}.", file=discord.File(f"{user_id}.{sink.encoding}"))

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

        await asyncio.sleep(10)

        vc.stop_recording()
        
        await ctx.send("Stopped recording ( AUTO )")

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