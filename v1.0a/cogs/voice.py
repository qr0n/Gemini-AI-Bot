import discord
import asyncio
import json
import os
import typing

from discord.ext import commands, tasks
from discord import AllowedMentions
from typing import Dict
from modules.BotModel import BotModel
from modules.DiscordBot import headless_Gemini

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

connections: Dict[int, discord.VoiceClient] = {}
connected = []
allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False, replied_user=False)

class TranscriptionCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    async def once_done(self, sink: discord.sinks, channel: discord.TextChannel, *args, ):  # Our voice client already passes these in.
        recorded_users = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items()]

        # await sink.vc.disconnect()  # Disconnect from the voice channel.

        for user_id, audio in sink.audio_data.items():
            file_name = f'./{user_id}.{sink.encoding}'

            with open(file_name, 'wb') as f:
                audio.file.seek(0)
                f.write(audio.file.read())
                f.close()

            file = await BotModel.upload_attachment(file_name) # Uploads
            stt = await BotModel.speech_to_text(audio_file=file) # Converts to text +1 

            author_name = await self.bot.get_or_fetch_user(user_id)

            text = await channel.send(f"What I got:\n```{author_name} : {stt}```", allowed_mentions=allowed_mentions)

            response = await headless_Gemini.generate_response(channel_id=channel.id, author_name=author_name, author_content=stt) # Responds to converted + 1
            await text.reply(response)
            
            # os.remove(file_name) # Deletes the recorded file

        #await channel.send(f"Finished recording audio for: {', '.join(recorded_users)}.", file=discord.File(f"{user_id}.{sink.encoding}"))

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
            self.once_done,
            ctx.channel
        )
        
        await ctx.send("Listening!")

        await asyncio.sleep(config["VOICE"]["record-time"])

        vc.stop_recording()
        
        await ctx.send("Hold on! Let me process... :thinking:")

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