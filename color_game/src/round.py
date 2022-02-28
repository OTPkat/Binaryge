import asyncio
from abc import ABC, abstractmethod
from discord.ui import Button, View

import discord
import time
from discord.ext import commands
from discord import Embed
from typing import Optional, Set, Dict
from collections import Counter
import random
import utils.emojis as animojis


class ColorGameRound(ABC):
    round_name: str
    emojis: Set[str]
    round_time: int = 30

    def __init__(
        self,
        allowed_player_ids: Optional[Set[str]],
        bot: commands.Bot,
        button_style: discord.ButtonStyle,
    ):
        self.allowed_player_ids = allowed_player_ids
        self.bot = bot
        self.button_style = button_style
        self.player_choices_message: Optional[discord.Message] = None
        self.color_choice_per_user_id: Optional[Dict[int, str]] = dict()

    def get_current_player_choices_embed(self):
        color_counts = Counter(self.color_choice_per_user_id.values())
        choices_embed = discord.Embed(
            title=f"{self.round_name} - Choices Distribution",
            description=f"There is currently a total of **{sum(color_counts.values())}** player(s).",
            color=0x0052FB,
        )
        for choice, amount in color_counts.items():
            choices_embed.add_field(name=choice, value=amount, inline=False)
        return choices_embed

    def get_view(self, filter_ids: Optional[Set[str]] = None) -> View:
        view = View()
        for emoji in self.emojis:
            button = Button(style=self.button_style, emoji=emoji, custom_id=emoji)

            async def button_callback(interaction: discord.Interaction):
                if (not filter_ids) or (interaction.user.id in filter_ids):
                    self.color_choice_per_user_id[
                        interaction.user.id
                    ] = interaction.data["custom_id"]
                    print(
                        f"user {interaction.user.id} chose color: {interaction.data['custom_id']}"
                    )
                    choices_embed = self.get_current_player_choices_embed()
                    if self.player_choices_message:
                        await self.player_choices_message.edit(embed=choices_embed)
                    else:
                        player_choices_message = await interaction.channel.send(
                            embed=choices_embed
                        )
                        self.player_choices_message = player_choices_message

            button.callback = button_callback
            view.add_item(button)
        return view

    @abstractmethod
    async def solve_round(self, ctx) -> Optional[Set[int]]:
        """
        :return: list of discord user id for next round
        """
        ...

    @abstractmethod
    def get_embed(self, end_time: int) -> Embed:
        ...

    async def start_round(self, ctx):
        await ctx.send(
            view=self.get_view(),
            embed=self.get_embed(end_time=int(time.time()) + self.round_time),
        )
        await asyncio.sleep(self.round_time)
        winner_ids = await self.solve_round(ctx=ctx)
        return winner_ids


class ColorGameFirstRound(ColorGameRound):
    round_name = "Follow them"
    emojis = {
        animojis.PEPE_CLAP,
        animojis.BONGO_LOVE,
        animojis.PEEPO_RIOT,
        animojis.BONGO_PEPE,
    }

    def __init__(self, allowed_player_ids: Optional[Set[str]], bot, button_style):
        super().__init__(allowed_player_ids, bot, button_style)

    def get_embed(self, end_time: int) -> Embed:
        embed = discord.Embed(
            title=f"{self.round_name}",
            description=f"The two most chosen emojis will lead you to the next game."
            " If only two or less emojis are chosen, 75% of you will be randomly eliminated.",
            color=0x0052FB,
        )
        embed.add_field(name="Choice Deadline", value=f"<t:{end_time}:R>")
        return embed

    async def start_round(self, ctx):
        await ctx.send(
            view=self.get_view(),
            embed=self.get_embed(end_time=int(time.time()) + self.round_time),
        )
        await asyncio.sleep(self.round_time)
        winner_ids = await self.solve_round(ctx=ctx)
        return winner_ids

    async def solve_round(self, ctx) -> Optional[Set[int]]:
        color_counts = Counter(self.color_choice_per_user_id.values())
        if not color_counts:
            embed = discord.Embed(
                title=f"Nobody played in time",
                description=f"No winners",
                color=0x0052FB,
            )
            await ctx.send(embed=embed)
            return set()

        elif len(color_counts) == 1:
            color1, count = color_counts.popitem()
            amount_players = color_counts[color1]
            winner_ids = random.sample(
                self.color_choice_per_user_id.keys(), max(1, int(0.25 * amount_players))
            )
            embed = discord.Embed(
                title=f"Time is up. {animojis.SCAM} Everybody chose {color1}, I will randomly eliminate 75% of you.",
                description=f"{color1}",
                color=0x0052FB,
            )
        elif len(color_counts) == 2:
            color1, color2 = color_counts.most_common(2)
            amount_players = color_counts[color1] + color_counts[color2]
            amount_of_winners = int(0.25 * amount_players)
            if not amount_of_winners:
                amount_of_winners = 1
            winner_ids = random.sample(
                self.color_choice_per_user_id.keys(), amount_of_winners
            )
            embed = discord.Embed(
                title=f"Time is up. {animojis.SCAM} Only two colors were chosen {animojis.SCAM}, I will randomly eliminate 75% of you.",
                description=f"Chosen Colors: w{color1[0]} and {color2[0]}",
                color=0x0052FB,
            )

        else:
            color1, color2 = color_counts.most_common(2)
            winner_ids = {
                user_id
                for user_id, color in self.color_choice_per_user_id.items()
                if color == color1[0] or color == color2[0]
            }
            embed = discord.Embed(
                title=f"Time is up. Winning colors are:",
                description=f"{color1[0]} and {color2[0]}",
                color=0x0052FB,
            )

        winner_members = await asyncio.gather(
            *[self.bot.fetch_user(user_id) for user_id in winner_ids]
        )
        embed.add_field(
            name="Players proceeding to the next round:",
            value=" ".join([x.mention for x in winner_members]),
        )
        await ctx.send(embed=embed)
        return winner_ids


class ColorGameSecondRound(ColorGameRound):
    round_name = "Hide out"
    emojis = {animojis.PEPE_JAM, animojis.HACKERMANS, animojis.GAMBAGE, animojis.HYPERS}

    def __init__(self, allowed_player_ids: Set[str], bot, button_style):
        super().__init__(allowed_player_ids, bot, button_style)

    def get_embed(self, end_time: int) -> Embed:
        embed = discord.Embed(
            title=f"{self.round_name}",
            description="The two least chose emojis will lead you to the next game."
            "If only two or less emojis are chosen, 75% of you will be randomly eliminated",
            color=0x0052FB,
        )
        embed.add_field(name="Choice Deadline", value=f"<t:{end_time}:R>")
        return embed

    async def solve_round(self, ctx):
        color_counts = Counter(self.color_choice_per_user_id.values())
        if not color_counts:
            embed = discord.Embed(
                title=f"Nobody played in time",
                description=f"No winners",
                color=0x0052FB,
            )
            await ctx.send(embed=embed)
            return {}

        elif len(color_counts) == 1:
            color1, count = color_counts.popitem()
            amount_players = color_counts[color1]
            winner_ids = random.sample(
                self.color_choice_per_user_id.keys(), max(1, int(0.25 * amount_players))
            )
            embed = discord.Embed(
                title=f"Time is up. Everybody chose {color1}, I will randomly eliminate 75% of you.",
                description=f"{color1}",
                color=0x0052FB,
            )

        elif len(color_counts) == 2:
            color1, color2 = color_counts.most_common(2)
            amount_players = color_counts[color1] + color_counts[color2]
            amount_of_winners = int(0.25 * amount_players)
            if not amount_of_winners:
                amount_of_winners = 1
            winner_ids = random.sample(
                self.color_choice_per_user_id.keys(), amount_of_winners
            )
            embed = discord.Embed(
                title=f"Time is up. {animojis.SCAM} Only two colors were chosen {animojis.SCAM}, I will randomly eliminate 75% of you.",
                description=f"Chosen colors: {color1[0]} and {color2[0]}",
                color=0x0052FB,
            )

        else:
            color1, color2 = color_counts.most_common()[-2:]
            winner_ids = {
                user_id
                for user_id, color in self.color_choice_per_user_id.items()
                if color == color1[0] or color == color2[0]
            }
            embed = discord.Embed(
                title=f"Time is up. Winning colors are:",
                description=f"{color1[0]}  and {color2[0]}",
                color=0x0052FB,
            )

        winner_members = await asyncio.gather(
            *[self.bot.fetch_user(user_id) for user_id in winner_ids]
        )
        embed.add_field(
            name="Players proceeding to the next round:",
            value=" ".join([x.mention for x in winner_members]),
            inline=False,
        )
        await ctx.send(embed=embed)
        return winner_ids
