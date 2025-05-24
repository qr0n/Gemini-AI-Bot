import json
import asyncio

from discord.ext import commands
from modules.DiscordBot import Gemini
from modules.CommonCalls import CommonCalls
from modules.ManagedMessages import ManagedMessages
from discord import Message, AllowedMentions, Reaction, Member

allowed_mentions = AllowedMentions(everyone=False, users=False, roles=False)
activation_path = f"/app/data/{CommonCalls.config()['alias']}-activation.json"


class GeminiCog(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    def is_activated(self, channel_id) -> bool:
        try:
            with open(activation_path, "r") as ul_activation:
                activated: dict = json.load(ul_activation)
                print(
                    "Activated channels function call `is_activated` (Message from line 22 @ cogs/gemini.py)"
                )
                return bool(activated.get(str(channel_id), False))
        except FileNotFoundError:
            with open(activation_path, "w") as E:
                E.write("{}")
                E.close()

    @commands.Cog.listener("on_message")
    async def listen(self, message: Message):
        channel_id = message.channel.id

        if message.author.id == self.bot.user.id:
            return

        if self.bot.user.mentioned_in(message) or self.is_activated(channel_id):
            pass
        else:
            return

        async with message.channel.typing():
            await asyncio.sleep(2)

        response = await Gemini.generate_response(
            message, await self.bot.get_context(message)
        )

        if response == "[]":
            return await message.reply(CommonCalls.config()["error_message"])

        chunks = [response[i : i + 2000] for i in range(0, len(response), 2000)]

        for chunk in chunks:
            try:
                text = await message.reply(
                    chunk, mention_author=False, allowed_mentions=allowed_mentions
                )
                await ManagedMessages.add_to_message_list(
                    channel_id=channel_id,
                    message_id=text.id,
                    message=f"{CommonCalls.load_character_details()['name']}: {text.content}",
                )
            except Exception as E:
                print(f"Error replying response: {E}")

    @commands.Cog.listener("on_reaction_add")
    async def on_rxn_add(self, reaction: Reaction, user: Member):
        channel_id = reaction.message.channel.id

        match reaction.emoji:

            case "🔇":
                await ManagedMessages.remove_from_message_list(
                    channel_id, reaction.message.id
                )
                print(f"Removed message ID ({reaction.message.id}) from STM")

            # case "⭐":
            #     await ManagedMessages.save_message_to_db(message_content=reaction.message.content, message_id=reaction.message.id, jump_url=reaction.message.jump_url)
            #     print("Saved message to `bot_db`")

            case "🗑️":
                await ManagedMessages.remove_message_from_db(
                    message_id=reaction.message.id
                )

            case _:

                if (
                    reaction.message.author.id is not self.bot.user.id
                    and not reaction.is_custom_emoji()
                ):
                    return

                if channel_id not in ManagedMessages.context_window:
                    ManagedMessages.context_window[channel_id] = []
                    print(reaction.emoji)

                await ManagedMessages.add_to_message_list(
                    channel_id,
                    reaction.message.id,
                    f"{user.name} reacted with '{reaction.emoji}' to your message '{reaction.message.content}'",
                )


def setup(bot: commands.Bot):
    bot.add_cog(GeminiCog(bot))
