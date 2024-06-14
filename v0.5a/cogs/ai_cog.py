import json
from discord.ext import commands
from discord import Message
from modules.Memories import Memories
from modules.ContextWindow import ContextWindow
from modules.BotModel import BotModel

context_window = ContextWindow().context_window

with open("./config.json", "r") as ul_config:
    config = json.load(ul_config)

class Messager(commands.Cog, name="Gemini AI Bot"):
    
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener('on_message')
    async def message_generator(self, msg : Message):

        character_name = Memories.load_character_details()["name"]

        if msg.author.id == self.bot.user.id:
            return

        if not self.bot.user.mentioned_in(msg):
            return

        try:
            ctx = await self.bot.get_context(msg)
        except Exception as e:
            print(f"Error getting context: {e}")
            return

        user_id = f"{msg.guild.id}-{msg.author.id}"

        if user_id not in context_window:
            context_window[user_id] = []

        context_window[user_id].append(f"{msg.author.name}: {msg.content}")

        if len(context_window[user_id]) > config["MAX_CONTEXT_WINDOW"]:  # Adjust the window size as needed
            context_window[user_id].pop(0)
            print(context_window)

        await ctx.channel.typing()

        remembered_memories = Memories().compare_memories(user_id, msg.content)
        try:
            if remembered_memories['is_similar']:
                prompt = BotModel.read_prompt(msg, remembered_memories['similar_phrase'])
            else:
                prompt = BotModel.read_prompt(msg)
        except Exception:
            print()
        print(remembered_memories)
        print(prompt)
        response = BotModel.generate_content(prompt, user_id=user_id)
        Memories().save_to_memory(msg)
    
        # Strip bot's name from the final response before replying it
        if response.startswith(f"{character_name}: "):
                response = response[len(f"{character_name}: "):]

        chunks = [response[i:i + 2000] for i in range(0, len(response), 2000)]

        for chunk in chunks:
            try:
                await ctx.reply(chunk, mention_author=False)
            except Exception as E:
                print(f"Error replying response: {E}")
