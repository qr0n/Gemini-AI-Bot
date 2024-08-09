import json
import discord
from discord.ext import commands
from discord.ext.commands import Context
from modules.ManagedMessages import ManagedMessages
from modules.Memories import Memories

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

class AIController(commands.Cog, name='AI-Controller'):
    '''These commands are used to control the AI'''

    def __init__(self, bot):
        self.bot : commands.Bot = bot

    @commands.command()
    async def wack(self, ctx : Context):
        """Clears the bot's context window, resetting the conversation"""
        await ctx.reply(await ManagedMessages.remove_channel_from_list(ctx.channel.id))
    
    @commands.command()
    async def activate(self, ctx : Context):
        """Activates the bot in a channel causing it to reply to EVERY message"""
        with open("./activation.json", "r") as unloaded_activated_channel:
            activated_channels = json.load(unloaded_activated_channel)
            activated_channels[ctx.channel.id] = True

        with open("./activation.json", "w") as unloaded_activated_channel:
            json.dump(activated_channels, unloaded_activated_channel)

            activated_string = config["MESSAGES"]["activated_message"] or f"{self.bot.user.name} is activated in <#{ctx.channel.id}>"
            await ctx.reply(activated_string, mention_author=False)

    @commands.command()
    async def deactivate(self, ctx : Context):
        """Removes the bot from the activated channels causing it to stop replying to every messge, but still on mention"""
        with open("./activation.json", "r") as unloaded_activated_channel:
            activated_channels = json.load(unloaded_activated_channel)
            del activated_channels[str(ctx.channel.id)]

        with open("./activation.json", "w") as unloaded_activated_channel:
            json.dump(activated_channels, unloaded_activated_channel)

            activated_string = config["MESSAGES"]["deactivated_message"] or f"{self.bot.user.name} has deactivated in <#{ctx.channel.id}>"
            await ctx.reply(activated_string, mention_author=False)

    @commands.command()
    async def remember(self, ctx : Context):
        """Forcefully calls the save_to_memory function [MAY NOT WORK AS EXPECTED]"""
        await Memories().save_to_memory(message=ctx.message, force=True)
        await ctx.reply("force remembered ._.")

    @commands.command()
    async def connect(self, ctx : Context , channel : discord.VoiceChannel = None):
        """Joins a voice channel."""

        destination = channel if channel else ctx.author.voice.channel # CHOOSING THE DESTINATION, MIGHT BE THE REQUESTED ONE, BUT IF NOT THEN WE PICK AUTHORS VOICE CHANNEL

        if ctx.voice_client: # CHECKING IF THE BOT IS PLAYING SOMETHING
            await ctx.voice_state.voice.move_to(destination) # IF THE BOT IS PLAYING WE JUST MOVE THE BOT TO THE DESTINATION
            return

        await destination.connect() # CONNECTING TO DESTINATION
        await ctx.send(f"Succesfully joined the voice channel: {destination.name} ({destination.id}).")

    @commands.command()
    async def play(self, ctx : Context, channel : discord.VoiceChannel = None):
        destination = channel if channel else ctx.author.voice.channel # CHOOSING THE DESTINATION, MIGHT BE THE REQUESTED ONE, BUT IF NOT THEN WE PICK AUTHORS VOICE CHANNEL

        if ctx.voice_client: # CHECKING IF THE BOT IS PLAYING SOMETHING
            await ctx.voice_state.voice.move_to(destination) # IF THE BOT IS PLAYING WE JUST MOVE THE BOT TO THE DESTINATION
            return
        
        await destination.connect() # CONNECTING TO DESTINATION
        await ctx.send(f"Succesfully joined the voice channel: {destination.name} ({destination.id}).")
        

def setup(bot : commands.Bot):
    bot.add_cog(AIController(bot))