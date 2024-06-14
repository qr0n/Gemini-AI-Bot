import discord
from discord.ext import commands
import os

class DevCommands(commands.Cog, name='Developer Commands'):
	'''These are the developer commands'''

	def __init__(self, bot):
		self.bot = bot
		print("Cog Manager Loaded")

	async def cog_check(self, ctx):  
		'''
		The default check for this cog whenever a command is used. Returns True if the command is allowed.
		'''
		return ctx.author.id == self.bot.owner_id

	@commands.command(  # Decorator to declare where a command is.
		name='reload',  # Name of the command, defaults to function name.
		aliases=['rl']  # Aliases for the command.
	)  
	async def reload(self, ctx, cog):
		'''
		Reloads a cog.
		'''
		extensions = self.bot.extensions  # A list of the bot's cogs/extensions.
		if cog == 'all':  # Lets you reload all cogs at once
			for extension in extensions:
				await self.bot.unload_extension(extension)
				await self.bot.load_extension(extension)
				await ctx.send(f"Reloaded `{extension}`")
		if cog in extensions:
			await self.bot.unload_extension(cog)  # Unloads the cog
			await self.bot.load_extension(cog)  # Loads the cog
			await ctx.send(f'Reloaded `{cog}`')  # Sends a message where content='Done'


	@commands.command(name="unload", aliases=['ul']) 
	async def unload(self, ctx, cog):
		'''
		Unload a cog.
		'''
		extensions = self.bot.extensions
		if cog == "cogs.main_cog":
			return await ctx.send("You cannot unload the main cog")
		if cog not in extensions:
			await ctx.send("Cog is not loaded!")
			return
		await self.bot.unload_extension(cog)
		await ctx.send(f"`{cog}` has successfully been unloaded.")
	
	@commands.command(name="load", aliases=["l"])
	async def load(self, ctx, cog):
		'''
		Loads a cog.
		'''
		try:

			await self.bot.load_extension(cog)
			await ctx.send(f"`{cog}` has successfully been loaded.")

		except commands.errors.ExtensionNotFound:
			await ctx.send(f"`{cog}` does not exist!")

	@commands.command(name="listcogs", aliases=['lc'])
	async def listcogs(self, ctx):
		'''
		Returns a list of all enabled commands.
		'''
		base_string = "```css\n"  # Gives some styling to the list (on pc side)
		base_string += "\n".join([str(cog) for cog in self.bot.extensions])
		base_string += "\n```"
		await ctx.send(embed=discord.Embed.from_dict({
      "title" : "Current Loaded Cogs",
    "description" : f"{base_string}"
    }))
  

async def setup(bot):
	await bot.add_cog(DevCommands(bot))