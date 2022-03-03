import asyncio
import time

import typing
import discord
import logging
import utils.emojis as animojis
from typing import Optional, Dict
from utils.command_check import only_owners, OWNERS
from discord.ext import commands
from color_game.src.round import (
    TwoMostChosenWin,
    TwoLeastChosenWin,
    MostChosenWin,
    LeastChosenWin,
    ColorGameRound,
    TwoLeastChosenLoose,
)

TIME_BETWEEN_LEVEL = 30

ROUND_QUEUE: typing.List[typing.Type[ColorGameRound]] = [
    TwoLeastChosenLoose,
    TwoMostChosenWin,
    MostChosenWin,
    TwoLeastChosenWin,
    LeastChosenWin,
]


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

    async def get_introductory_embed(self):
        dornick = await self.bot.fetch_user(914457549116411924)
        embed = discord.Embed(
            title=f"{animojis.BONGO_PEPE} Peepo Experiment {animojis.BONGO_PEPE}",
            description=f"Welcome to the refined version of {dornick.mention}'s favorite experiment,"
            f" the **Peepo Experiment** {animojis.GAMBAGE}.\n"
            "The Peepo Experiment consists of several rounds in which you will have to **choose an emoji**, the winners will be determined"
            f" on a rule that will **vary on each round**... Anyone can join the first round of an Experiment, the following rounds will be "
            f" accessible only to the winners. If you don't submit your choice in time you will be eliminated {animojis.PEEPO_RIOT}.\n"
            f"You may team up {animojis.BONGO_LOVE}, betray friends {animojis.SCAM}, and basically do anything you think of"
            f" to make your way out of the Peepo Experiment {animojis.CIGAR} ... or you will rest in peace {animojis.DEADGE}",
            color=0x0052FB,
        )
        return embed

    def get_break_embed(self, time_until_start: int):
        embed = discord.Embed(
            title=f"{animojis.BEDGE} Peepo Break {animojis.BEDGE}",
            description=f"{animojis.SLEEP} You can rest until next round {animojis.SLEEP}",
            color=0x0052FB,
        )
        embed.add_field(name="Next round", value=f"<t:{time_until_start}:R>")
        return embed

    async def get_winner_embed(self, winner_id: Optional[int] = None):
        if winner_id:
            winner = await self.bot.fetch_user(winner_id)
            embed = discord.Embed(
                title=f" {animojis.BONGO_LOVE} Peepo Experiment Winner {animojis.BONGO_LOVE}",
                description=f"{animojis.HYPES} {animojis.HYPERS} {winner.mention} {animojis.HYPERS} {animojis.HYPES}",
                color=0x0052FB,
            )

            admins = await asyncio.gather(
                *[self.bot.fetch_user(owner) for owner in OWNERS]
            )
            admin_mention = " ".join([admin.mention for admin in admins])
            embed.add_field(
                name=f"Reward {animojis.CIGAR}",
                value=f"Contact one of the admins for the reward: {admin_mention}",
            )
        else:
            embed = discord.Embed(
                title=f"{animojis.SCAM} Peepo Experiment Ended {animojis.SCAM}",
                description=f"No winners this time, see you next batch",
                color=0x0052FB,
            )
        return embed

    @commands.check(only_owners)
    @commands.command()
    async def start_color_game(self, ctx, delay=0):

        await ctx.message.channel.purge(limit=2000)
        try:
            delay = 60 * 60 * int(delay)
        except ValueError:
            delay = 0
        intro_embed = await self.get_introductory_embed()
        iteration_start_date = int(time.time()) + delay
        intro_embed.add_field(
            name="Next batch of Peepo Experiments will start in",
            value=f"<t:{iteration_start_date}:R>",
        )
        winner_ids = None
        await ctx.send(embed=intro_embed)
        await asyncio.sleep(delay=delay)
        round_count = 0
        while True:
            for round_ in ROUND_QUEUE:
                round_count += 1
                winner_ids = await round_(
                    allowed_player_ids=winner_ids,
                    bot=self.bot,
                    button_style=discord.ButtonStyle.blurple,
                    round_name=f"Round {round_count}"
                ).start_round(ctx)
                if len(winner_ids) > 1:
                    await ctx.send(
                        embed=self.get_break_embed(
                            time_until_start=int(time.time()) + TIME_BETWEEN_LEVEL
                        )
                    )
                    await asyncio.sleep(TIME_BETWEEN_LEVEL)

                else:
                    if winner_ids:
                        winner_embed = await self.get_winner_embed(winner_ids.pop())
                    else:
                        winner_embed = await self.get_winner_embed()

                    await ctx.send(
                        "`" + "-" * 17 + f" Peepo Experiment Terminated " + "-" * 17 + "`",
                        embed=winner_embed
                    )
                    return
