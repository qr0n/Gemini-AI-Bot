from discord.ext import commands
from modules.VoiceCall import VoiceCalls


class voicechannel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.command()
    async def start_recording(self, ctx: commands.Context) -> None:
        await VoiceCalls.start_recording(ctx)

    @commands.command()
    async def stop_recording(self, ctx: commands.Context) -> None:
        await VoiceCalls.stop_recording(ctx)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(voicechannel(bot))
