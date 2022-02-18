import asyncio
import typing

import discord
import logging
from typing import Optional, Dict
from utils.command_check import only_owners
from discord.ext import commands
from color_game.src.round import ColorGameFirstRound, ColorGameSecondRound

TIME_BETWEEN_LEVEL = 15


class ColorGame(commands.Cog):
    def __init__(
            self,
            bot: commands.Bot,
            logger: logging.Logger,
            channel_name: str,
    ):
        self.bot = bot
        self.logger = logger
        self.message: Optional[discord.Message] = None
        self.sign_ups_queue: Optional[Dict[str, discord.User]] = {}
        self.channel_name = channel_name
        self.guild: Optional[discord.Guild] = None
        self.channel: Optional[discord.TextChannel] = None

    @commands.check(only_owners)
    @commands.command()
    async def start_color_game(self, ctx):
        winner_ids = await ColorGameFirstRound(allowed_player_ids=set(), bot=self.bot).start_round(ctx)
        await ctx.send(f"You can rest {TIME_BETWEEN_LEVEL // 60} minutes before next round.")
        await asyncio.sleep(TIME_BETWEEN_LEVEL)
        await ColorGameSecondRound(allowed_player_ids=winner_ids, bot=self.bot).start_round(ctx)
        await ctx.send(f"You can rest {TIME_BETWEEN_LEVEL // 60} minutes before next round.")
        await asyncio.sleep(TIME_BETWEEN_LEVEL)

