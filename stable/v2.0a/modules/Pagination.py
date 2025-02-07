import discord
from discord.ext import commands
from discord.ui import Button, View


class PaginatorView(View):
    def __init__(self, embeds: list[discord.Embed], timeout: int = 60):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self.message = None

        self.first_button = Button(label="⏮️", style=discord.ButtonStyle.secondary)
        self.prev_button = Button(label="◀️", style=discord.ButtonStyle.secondary)
        self.next_button = Button(label="▶️", style=discord.ButtonStyle.secondary)
        self.last_button = Button(label="⏭️", style=discord.ButtonStyle.secondary)

        self.first_button.callback = self.first_page
        self.prev_button.callback = self.prev_page
        self.next_button.callback = self.next_page
        self.last_button.callback = self.last_page

        self.add_item(self.first_button)
        self.add_item(self.prev_button)
        self.add_item(self.next_button)
        self.add_item(self.last_button)

    async def first_page(self, interaction: discord.Interaction):
        self.current_page = 0
        await self.update_message(interaction)

    async def prev_page(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_message(interaction)

    async def next_page(self, interaction: discord.Interaction):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await self.update_message(interaction)

    async def last_page(self, interaction: discord.Interaction):
        self.current_page = len(self.embeds) - 1
        await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            embed=self.embeds[self.current_page], view=self
        )

    async def on_timeout(self):
        if self.message:
            await self.message.edit(view=None)


async def paginate(ctx: commands.Context, embeds: list[discord.Embed]):
    view = PaginatorView(embeds)
    view.message = await ctx.send(embed=embeds[view.current_page], view=view)
