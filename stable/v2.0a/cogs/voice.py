from discord.ext import commands
from discord import Member, VoiceState
from modules.VoiceCall import VoiceCalls, connections


class voicechannel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.command()
    async def start_recording(self, ctx: commands.Context) -> None:
        await VoiceCalls.start_recording(ctx)

    @commands.command()
    async def stop_recording(self, ctx: commands.Context) -> None:
        await VoiceCalls.stop_recording(ctx)

    @commands.Cog.listener("on_voice_state_update")
    async def on_voice_state_update(
        self, member: Member, before: VoiceState, after: VoiceState
    ):
        if member.id == self.bot.id:
            return

        if (
            before.channel is not None and after.channel is None
        ):  # Detects if someone leaves
            print("PRE update connections", connections)
            del connections[member.guild.id]
            print("POST update connections", connections)

    @commands.command()
    async def what_conn(self, ctx: commands.Context) -> None:
        await ctx.send(connections)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(voicechannel(bot))
