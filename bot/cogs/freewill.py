import json
import random
import asyncio

from discord import Message, AllowedMentions
from discord.ext import commands
from modules.DiscordBot import Gemini
from modules.ManagedMessages import ManagedMessages
from modules.CommonCalls import CommonCalls

allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False)
activation_path = f"data/{CommonCalls.config()['alias']}-activation.json"


class Freewill(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot

    def is_activated(self, channel_id) -> bool:
        with open(activation_path, "r") as ul_activation:
            activated: dict = json.load(ul_activation)
            print(
                "[BOT][INFO] | Activated channels function call `is_activated` (Message from line 23 @ cogs/new_freewill.py)"
            )
            return bool(activated.get(str(channel_id), False))

    @commands.Cog.listener("on_message")
    async def freewill(self, message: Message) -> None:
        if CommonCalls.config()["freewill"] == "on":  # TODO implement

            ctx = await self.bot.get_context(message)

            if message.author.id == self.bot.user.id:
                return

            if self.bot.user.mentioned_in(message) or self.is_activated(ctx.channel.id):
                return

            text_frequency = float(CommonCalls.config().get("textFrequency", 0)) * 0.01
            keywords = CommonCalls.config().get("keywords", [])
            keyword_added_chance = 0

            for i in keywords:
                if i.lower() in message.content.lower():
                    keyword_added_chance = (
                        float(CommonCalls.config()["keywordChance"]) * 0.01
                    )

            if random.random() < min(text_frequency + keyword_added_chance, 1.0):
                response = await Gemini.generate_response(
                    message, await self.bot.get_context(message)
                )

                async with message.channel.typing():
                    await asyncio.sleep(2)  # artificial delay lol

                chunks = [response[i : i + 2000] for i in range(0, len(response), 2000)]

                for chunk in chunks:
                    try:
                        text = await message.reply(
                            chunk,
                            mention_author=False,
                            allowed_mentions=allowed_mentions,
                        )
                        await ManagedMessages.add_to_message_list(
                            channel_id=ctx.channel.id,
                            message_id=text.id,
                            message=f"{CommonCalls.load_character_details()['name']}: {text.content}",
                        )
                    except Exception as E:
                        print(f"Error replying response: {E}")

            # if random.random() < min(reaction_frequency + keyword_added_chance, 1.0):
            #     response = await Gemini.generate_response(message)

            #     async with message.channel.typing():
            #         await asyncio.sleep(2) # artificial delay lol

            #     await ctx.reply(response, mention_author=False, allowed_mentions=allowed_mentions)


def setup(bot: commands.Bot):
    bot.add_cog(Freewill(bot))
