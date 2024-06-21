import json
import random
from discord.ext import commands
from discord import Message, AllowedMentions
from modules.ContextWindow import ContextWindow
from modules.BotModel import BotModel, read_prompt
from modules.Memories import Memories
from PIL import Image

context_window = ContextWindow.context_window
allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False)

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

class Freewill(commands.Cog):
    def __init__(self, bot):
        self.bot : commands.Bot = bot
    
    @commands.Cog.listener("on_message")
    async def freewill(self, message : Message):
        if config["FREEWILL"]["enabled"]:
            if message.author.id == self.bot.user.id:
                return
            
            if self.bot.user.mentioned_in(message):
                return

            channel_id = message.channel.id
            text_frequency = config["FREEWILL"]["text_frequency"]
            reaction_frequency = config["FREEWILL"]["reaction_frequency"]
            keywords = config["FREEWILL"]["keywords"]
            keyword_multiplier = config["FREEWILL"]["keywords_multiplier"]
            
            if channel_id not in context_window:
                context_window[message.channel.id] = []
            
            if len(context_window[channel_id]) > config["MAX_CONTEXT_WINDOW"]:
                context_window[channel_id].pop(0)

            context_window[message.channel.id].append(f"{message.author.display_name}: {message.content}")


            if random.random() < text_frequency:
                prompt_plus = "You are now engaging or adding your own thoughts to this conversation, keep your reply as short as possible but make sure it makes sense and is relevant to the current topic. You will never roleplay as someone you are not instructed to roleplay as, you will use the language last used in your context window to make a response. You must not assume the conversation relates to you."

                remembered_memories = Memories().compare_memories(channel_id, message.content)
                if remembered_memories["is_similar"]:
                    prompt = read_prompt(message, remembered_memories['similar_phrase'])
                else:
                    prompt = read_prompt(message)

                await message.channel.typing()

                if message.attachments:
                    save_name = f"{message.guild.id}-{message.id}-{message.attachments[0].filename}"
                    await message.attachments[0].save(save_name)
                    image = Image.open(save_name)
                    full_prompt = prompt_plus
                    await message.reply(BotModel.generate_content(full_prompt, channel_id, image), mention_author=False, allowed_mentions=allowed_mentions)
                    image.close() # download attachments[0] in `attachments`
                else:
                    await message.reply(BotModel.generate_content(prompt, channel_id), mention_author=False, allowed_mentions=allowed_mentions)

            if random.random() < reaction_frequency:
                prompt_plus = "You are 'Sponge'. You have been given the ability to be allowed to express your current thoughts on this conversation via means of a reaction, use any standard emoji to react you must use unicode to react, you can only use ONE emoji to react you MUST represent this emoji in unicode ()"
                
                if message.attachments:
                    save_name = f"{message.guild.id}-{message.id}-{message.attachments[0].filename}"
                    await message.attachments[0].save(save_name)
                    image = Image.open(save_name)
                    content = BotModel.generate_reaction(prompt_plus, channel_id[channel_id], image)
                    print("space" + content + "space")
                    await message.add_reaction(content)
                    image.close() # download attachments[0] in `attachments` 
                else:
                    content = BotModel.generate_reaction(prompt_plus, context_window[channel_id])
                    print("space" + content + "space")
                    await message.add_reaction(content)

async def setup(bot : commands.Bot):
    await bot.add_cog(Freewill(bot))