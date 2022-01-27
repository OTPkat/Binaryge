import datetime
import random
from src.utils import BinaryUtils
import discord
from discord.ext import commands
import logging
from typing import Optional, Dict
from schemas.match import Match

# https://discord.com/api/oauth2/authorize?client_id=935134455054602240&permissions=8&scope=bot


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
        match_channel = await self.create_match_channel(
            member_1=member_1, member_2=member_2, guild=guild
        )
        match_embed = self.get_start_match_embed(
            starting_member=starting_member, n=n
        )
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
            current_player=starting_member,
            first_player=starting_member,
            amount_of_1_on_board=BinaryUtils.count_ones_in_binary_from_int(n),
            amount_of_0_on_board=BinaryUtils.count_zeros_in_binary_from_int(n),
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
    def get_start_match_embed(
        starting_member: discord.Member, n: int
    ):
        description = f"The game will start with n={BinaryUtils.int_to_binary_string(n)}. {starting_member.mention} you start!"
        embed_match = discord.Embed(
            title="Bynaryge's Match",
            description=description,
            color=0x00F0FF,
        )

        embed_match.add_field(
            name=f"Amount of 1 written on the binary Board",
            value=f"{BinaryUtils.count_ones_in_binary_from_int(n)}",
            inline=False,
        )

        embed_match.add_field(
            name="Current sum in binary representation",
            value=BinaryUtils.int_to_binary_string(n),
            inline=False,
        )
        return embed_match

    @commands.Cog.listener()
    async def bym(self, ctx, submitted_binary_number: str):
        if ctx.channel.id in self.matches_per_channel_id:
            if (
                ctx.author.id
                == self.matches_per_channel_id[ctx.channel.id].current_player
            ):
                if BinaryUtils.is_positive_binary_string(submitted_binary_number):
                    if self.matches_per_channel_id[ctx.channel.id].check_addition(
                        submitted_binary_number=submitted_binary_number
                    ):
                        self.matches_per_channel_id[ctx.channel.id].add(
                            submitted_binary_number=submitted_binary_number
                        )
                        self.matches_per_channel_id[
                            ctx.channel.id
                        ].last_update = datetime.datetime.now()
                        if not self.matches_per_channel_id[
                            ctx.channel.id
                        ].is_finished():
                            self.matches_per_channel_id[
                                ctx.channel.id
                            ].update_current_player()
                            await self.matches_per_channel_id[ctx.channel.id].update_embed_match()
                            await ctx.send(
                                f"Valid play by {ctx.author.mention}, {self.matches_per_channel_id[ctx.channel.id].current_player.mention}, your turn!"
                            )
                        else:
                            # todo send to db before deleting
                            self.matches_per_channel_id.pop(ctx.channel.id, None)
                            await ctx.send(
                                f"Match ended with {ctx.author.mention} as winner :gladge: :hackermange:"
                            )


def setup(bot):
    loader = bot.get_cog("Loader")
    bot.add_cog(
        MatchHandler(
            bot=bot,
            logger=loader.logger,
            category_name="binaryge",
        )
    )
