import random

import discord
from discord.ext import commands
import logging
from typing import Optional, Dict
from schemas.match import Match


class MatchHandler(commands.Cog):
    game_name: str = "bynaryge"

    def __init__(
        self,
        bot: commands.Bot,
        logger: logging.Logger,
        category_name: str,
    ):
        self.bot = bot
        self.logger = logger
        self.category_name = category_name
        self.matches_per_channel_id: Optional[Dict[str, Match]] = {}

    async def create_match(
        self, member_1: discord.Member, member_2: discord.Member, guild: discord.Guild
    ):
        match_channel = await self.create_match_channel(member_1=member_1, member_2=member_2, guild=guild)
        match_embed, n = self.get_start_match_embed(member_1=member_1, member_2=member_2)
        match_message = await match_channel.send(embed=match_embed)
        self.matches_per_channel_id[match_channel.id] = Match(
            channel=match_channel,
            member_1=member_1,
            member_2=member_2,
            message=match_message,
            n=n,
            current_sum=0
        )

    async def create_match_channel(
        self, member_1: discord.Member, member_2: discord.Member, guild: discord.Guild
    ):
        overwrites = {
            member_1: discord.PermissionOverwrite(
                read_messages=True, send_messages=True
            ),
            member_2: discord.PermissionOverwrite(
                read_messages=True, send_messages=True
            ),
        }
        channel = await guild.create_text_channel(
            f"{self.game_name}-{str(member_1)[:5]}-{str(member_2)[:5]}",
            overwrites=overwrites,
        )
        return channel

    @staticmethod
    def get_start_match_embed(member_1: discord.Member, member_2: discord.Member):
        u = random.randint(0, 1)
        n = random.randint(100, 10000)
        base_description = f"The game will start with n={'{0:b}'.format(n)}"
        if u:
            base_description += f"{member_1.mention}"
        else:
            base_description += f"{member_2.mention}"
        embed_match = discord.Embed(
            title="Bynaryge's Match",
            description=base_description,
            color=0x00F0FF,
        )
        return embed_match, n

    @commands.Cog.listener()
    async def bym(self):
        pass


def setup(bot):
    loader = bot.get_cog("Loader")
    bot.add_cog(
        MatchHandler(
            bot=bot,
            logger=loader.logger,
            category_name="binaryge",
        )
    )
