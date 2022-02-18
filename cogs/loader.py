from discord.ext import commands
import logging
from utils.command_check import only_owners


class Loader(commands.Cog):
    def __init__(self, bot: commands.Bot, logger: logging.Logger):
        self.bot = bot
        self.logger = logger

    @commands.command()
    @commands.check(only_owners)
    async def reload_cog(self, ctx, module):
        try:
            self.bot.reload_extension(module)
        except Exception as e:
            await ctx.send(f"Error when trying to reload cog : {e}")
        else:
            await ctx.send(f"Cog {module} reloaded")

    @commands.command()
    @commands.check(only_owners)
    async def unload_cog(self, ctx, module):
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await ctx.send(f"Error when trying to unload cog : {e}")
        else:
            await ctx.send(f"Cog {module} unloaded")

    @commands.command()
    @commands.check(only_owners)
    async def load_cog(self, ctx, module):
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.send(f"Error when trying to load cog : {e}")
        else:
            await ctx.send(f"Cog {module} loaded")
