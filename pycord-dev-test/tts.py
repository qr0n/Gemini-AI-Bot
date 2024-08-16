from discord import Intents, VoiceChannel, VoiceClient
import discord
from discord.ext import commands
from elevenlabs.client import ElevenLabs
from elevenlabs import play, stream, save
import io
import asyncio

intents = Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)

client = ElevenLabs(api_key="sk_676c1fb5c5d808e3c9fceca08b425d1914ae947c75dacd59")

async def say_with_elevenlabs(voice_channel, text, voice="Antoni"):
    # Generate audio
    _audio = client.generate(text=text, voice=voice, model="eleven_multilingual_v2")

    audio = stream(_audio)

    # Convert audio to a file-like object
    audio_file = io.BytesIO(audio)
    
    # Connect to the voice channel
    voice_client = await voice_channel.connect()
    
    # Play the audio
    voice_client.play(discord.FFmpegPCMAudio(audio_file, pipe=True))
    
    # Wait until the audio finishes playing
    while voice_client.is_playing():
        await asyncio.sleep(1)
    
    # Disconnect from the voice channel
    await voice_client.disconnect()

@bot.command()
async def speak(ctx, *, message):
    if ctx.author.voice:
        await say_with_elevenlabs(ctx.author.voice.channel, message)
    else:
        await ctx.send("You need to be in a voice channel to use this command.")

bot.run("MTI0NTkyMTYwOTQzMzQ4MTIzNg.G3zoR3.kwcqqOa--Fz5mzGwPQwvB-4BEhxdcwAQ0y2cqw")