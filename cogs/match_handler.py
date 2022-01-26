import datetime
import random
from src.utils import is_positive_binary_string
import discord
from discord.ext import commands
import logging
from typing import Optional, Dict
from schemas.match import Match
#https://discord.com/api/oauth2/authorize?client_id=935134455054602240&permissions=8&scope=bot


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
        u = random.randint(0, 1)
        n = random.randint(100, 10000)
        if u:
            starting_member = member_1
        else:
            starting_member = member_2
        match_channel = await self.create_match_channel(member_1=member_1, member_2=member_2, guild=guild)
        match_embed = self.get_start_match_embed(starting_member=starting_member, n=n, current_sum=n)
        match_message = await match_channel.send(embed=match_embed)
        self.matches_per_channel_id[match_channel.id] = Match(
            channel=match_channel,
            member_1=member_1,
            member_2=member_2,
            message=match_message,
            n=n,
            current_sum=n,
            start_date=datetime.datetime.now(),
            last_update=datetime.datetime.now(),
            current_player=starting_member
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
    def get_start_match_embed(starting_member:  discord.Member, n:int, current_sum: int):
        description = f"The game will start with n={'{0:b}'.format(n)}. {starting_member.mention} you start"
        embed_match = discord.Embed(
            title="Bynaryge's Match",
            description=description,
            color=0x00F0FF,
        )
        embed_match.add_field(
            name="Current sum",
            value=str(current_sum),
            inline=False,
        )
        embed_match.add_field(
            name="Current sum in binary representation",
            value='{0:b}'.format(current_sum),
            inline=False,
        )
        return embed_match

    def get_embed_from_match(self, match: Match):
        description = f"The game is going on with n={'{0:b}'.format(match.n)}. {match.current_player.mention} your turn"
        embed_match = discord.Embed(
            title="Bynaryge's Match",
            description=description,
            color=0x00F0FF,
        )
        embed_match.add_field(
            name="Current sum",
            value=str(match.current_sum),
            inline=False,
        )
        embed_match.add_field(
            name="Current sum in binary representation",
            value='{0:b}'.format(match.current_sum),
            inline=False,
        )
        return embed_match

    @commands.Cog.listener()
    async def bym(self, ctx, submitted_binary_number: str):
        if ctx.channel.id in self.matches_per_channel_id:
            if ctx.author.id == self.matches_per_channel_id[ctx.channel.id].current_player:
                if is_positive_binary_string(submitted_binary_number):
                    if self.matches_per_channel_id[ctx.channel.id].check_addition(submitted_binary_number=submitted_binary_number):
                        # todo update all metadata of the match
                        # todo check if no move left
                        self.matches_per_channel_id[ctx.channel.id].add(submitted_binary_number=submitted_binary_number)
                        self.matches_per_channel_id[ctx.channel.id].update_current_player()
                        self.matches_per_channel_id[ctx.channel.id].last_update = datetime.datetime.now()
                        updated_embed = self.get_embed_from_match(self.matches_per_channel_id[ctx.channel.id])
                        await self.matches_per_channel_id[ctx.channel.id].message.edit(embed=updated_embed)
                        await ctx.send(f"Valid play by {ctx.author.mention}")
            else:
                await ctx.send(f"It's not your turn")


def setup(bot):
    loader = bot.get_cog("Loader")
    bot.add_cog(
        MatchHandler(
            bot=bot,
            logger=loader.logger,
            category_name="binaryge",
        )
    )
