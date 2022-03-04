import asyncio
from abc import ABC, abstractmethod
from discord.ui import Button, View

import discord
import time
from discord.ext import commands
from discord import Embed
from typing import Optional, Set, Dict, Tuple
from collections import Counter
import random
import utils.emojis as animojis


class ColorGameRound(ABC):
    emojis: Set[str]
    round_time: int = 30

    def __init__(
        self,
        allowed_player_ids: Optional[Set[str]],
        bot: commands.Bot,
        button_style: discord.ButtonStyle,
        round_name: str
    ):
        self.allowed_player_ids = allowed_player_ids
        self.bot = bot
        self.button_style = button_style
        self.round_name = round_name
        self.player_choices_message: Optional[discord.Message] = None
        self.color_choice_per_user_id: Optional[Dict[int, str]] = dict()

    @abstractmethod
    def get_embed(self, end_time: int) -> Embed:
        ...

    @abstractmethod
    def get_winner_ids(self, color_counts: Counter) -> Tuple[Optional[Set[str]], Embed]:
        ...

    async def solve_round(self, ctx) -> Optional[Set[int]]:
        color_counts = Counter(self.color_choice_per_user_id.values())
        winner_ids, embed = self.get_winner_ids(color_counts=color_counts)
        winner_members = await asyncio.gather(
            *[self.bot.fetch_user(user_id) for user_id in winner_ids]
        )
        if winner_members:
            embed.add_field(
                name="Players proceeding to the next round:",
                value=" ".join([x.mention for j, x in enumerate(winner_members) if j < 30]) + " ...",
            )
        await ctx.send(embed=embed)
        return winner_ids

    def get_current_player_choices_embed(self):
        color_counts = Counter(self.color_choice_per_user_id.values())
        choices_embed = discord.Embed(
            title=f"{animojis.NERDGE} {self.round_name} - Choices Distribution {animojis.NERDGE}",
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

    async def start_round(self, ctx):
        await ctx.send(
            "`" + "-"*27 + f" {self.round_name} " + "-"*27 + "`",
            view=self.get_view(self.allowed_player_ids),
            embed=self.get_embed(end_time=int(time.time()) + self.round_time),
        )
        await asyncio.sleep(self.round_time)
        winner_ids = await self.solve_round(ctx=ctx)
        return winner_ids


class TwoMostChosenWin(ColorGameRound):
    emojis = {
        animojis.PEPE_CLAP,
        animojis.BONGO_LOVE,
        animojis.PEEPO_RIOT,
        animojis.BONGO_PEPE,
    }

    def __init__(self, allowed_player_ids: Optional[Set[str]], bot, button_style, round_name: str):
        super().__init__(allowed_player_ids, bot, button_style, round_name)

    def get_winner_ids(self, color_counts: Counter) -> Tuple[Optional[Set[str]], Embed]:
        winner_ids = set()
        if not color_counts:
            embed = discord.Embed(
                title=f"{animojis.DEADGE} Nobody played in time {animojis.DEADGE}",
                description=f"No winners",
                color=0x0052FB,
            )
        elif len(color_counts) == 1:
            color1, amount_players = color_counts.popitem()
            winner_ids = random.sample(
                self.color_choice_per_user_id.keys(), max(1, int(0.25 * amount_players))
            )
            embed = discord.Embed(
                title=f"{animojis.PEEPO_RIOT} Time is up {animojis.PEEPO_RIOT}",
                description=f"{animojis.SCAM} Everybody chose {color1}, I will randomly eliminate 75% of you.",
                color=0x0052FB,
            )
        elif len(color_counts) == 2:
            color1, color2 = color_counts.most_common(2)
            amount_players = color1[1] + color2[1]
            amount_of_winners = max(1, int(0.25 * amount_players))
            winner_ids = random.sample(
                self.color_choice_per_user_id.keys(), amount_of_winners
            )
            embed = discord.Embed(
                title=f"{animojis.PEEPO_RIOT} Time is up {animojis.PEEPO_RIOT}",
                description=f"{color1[0]} and {color2[0]} were the ony two chosen emojis {animojis.SCAM},"
                f" I will randomly eliminate 75% of you.",
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
                title=f"{animojis.PEEPO_RIOT} Time is up {animojis.PEEPO_RIOT}",
                description=f" Winning emojis are: {color1[0]} and {color2[0]}",
                color=0x0052FB,
            )
        return winner_ids, embed

    def get_embed(self, end_time: int) -> Embed:
        embed = discord.Embed(
            title=f"{animojis.BONGO_PEPE} {self.round_name} {animojis.BONGO_PEPE}",
            description=f"The two most chosen emojis will lead you to the next game."
            " If only two or less emojis are chosen, 75% of you will be randomly eliminated.",
            color=0x0052FB,
        )
        embed.add_field(name="Choice Deadline", value=f"<t:{end_time}:R>")
        return embed


class TwoLeastChosenWin(ColorGameRound):
    emojis = {animojis.PEPE_JAM, animojis.HACKERMANS, animojis.GAMBAGE, animojis.HYPERS}

    def __init__(self, allowed_player_ids: Set[str], bot, button_style, round_name):
        super().__init__(allowed_player_ids, bot, button_style, round_name)

    def get_winner_ids(self, color_counts: Counter) -> Tuple[Optional[Set[str]], Embed]:
        winner_ids = set()
        if not color_counts:
            embed = discord.Embed(
                title=f"{animojis.DEADGE} Nobody played in time {animojis.DEADGE}",
                description=f"No winners",
                color=0x0052FB,
            )

        elif len(color_counts) == 1:
            color1, amount_players = color_counts.popitem()
            winner_ids = random.sample(
                self.color_choice_per_user_id.keys(), max(1, int(0.25 * amount_players))
            )
            embed = discord.Embed(
                title=f"{animojis.PEEPO_RIOT} Time is up {animojis.PEEPO_RIOT}",
                description=f"Everybody chose {color1}, I will randomly eliminate 75% of you",
                color=0x0052FB,
            )

        elif len(color_counts) == 2:
            color1, color2 = color_counts.most_common(2)
            amount_players = color1[1] + color2[1]
            amount_of_winners = max(1, int(0.25 * amount_players))
            winner_ids = random.sample(
                self.color_choice_per_user_id.keys(), amount_of_winners
            )
            embed = discord.Embed(
                title=f"{animojis.PEEPO_RIOT} Time is up {animojis.PEEPO_RIOT}",
                description=f"{color1[0]} and {color2[0]} were the ony two chosen emojis {animojis.SCAM},"
                f" I will randomly eliminate 75% of you.",
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
                title=f"{animojis.PEEPO_RIOT} Time is up {animojis.PEEPO_RIOT}",
                description=f"Winning emojis are: {color1[0]}  and {color2[0]}",
                color=0x0052FB,
            )
        return winner_ids, embed

    def get_embed(self, end_time: int) -> Embed:
        embed = discord.Embed(
            title=f"{animojis.BONGO_PEPE} {self.round_name} {animojis.BONGO_PEPE}",
            description="The two least chosen emojis will lead you to the next game."
            " If only two or less emojis are chosen, 75% of you will be randomly eliminated",
            color=0x0052FB,
        )
        embed.add_field(name="Choice Deadline", value=f"<t:{end_time}:R>")
        return embed


class MostChosenWin(ColorGameRound):
    emojis = {animojis.PEPE_JAM, animojis.HACKERMANS, animojis.GAMBAGE, animojis.HYPERS}

    def __init__(self, allowed_player_ids: Set[str], bot, button_style, round_name):
        super().__init__(allowed_player_ids, bot, button_style, round_name)

    def get_embed(self, end_time: int) -> Embed:
        embed = discord.Embed(
            title=f"{animojis.BONGO_PEPE} {self.round_name} {animojis.BONGO_PEPE}",
            description="The most chosen emoji will lead you to the next game."
            "If only one emoji is chosen, 75% of you will be randomly eliminated",
            color=0x0052FB,
        )
        embed.add_field(name="Choice Deadline", value=f"<t:{end_time}:R>")
        return embed

    def get_winner_ids(self, color_counts: Counter) -> Tuple[Optional[Set[str]], Embed]:
        winner_ids = set()
        if not color_counts:
            embed = discord.Embed(
                title=f"{animojis.DEADGE} Nobody played in time {animojis.DEADGE}",
                description=f"No winners",
                color=0x0052FB,
            )

        elif len(color_counts) == 1:
            color1, count = color_counts.popitem()
            amount_players = count
            winner_ids = random.sample(
                self.color_choice_per_user_id.keys(), max(1, int(0.25 * amount_players))
            )
            embed = discord.Embed(
                title=f"{animojis.PEEPO_RIOT} Time is up {animojis.PEEPO_RIOT}",
                description=f"Everybody chose {color1}, I will randomly eliminate 75% of you.",
                color=0x0052FB,
            )

        else:
            winning_emoji = color_counts.most_common(1)[0][0]
            winner_ids = {
                user_id
                for user_id, emoji in self.color_choice_per_user_id.items()
                if emoji == winning_emoji
            }
            embed = discord.Embed(
                title=f"{animojis.PEEPO_RIOT} Time is up {animojis.PEEPO_RIOT}",
                description=f"Winning emoji is: {winning_emoji}",
                color=0x0052FB,
            )
        return winner_ids, embed


class LeastChosenWin(ColorGameRound):
    emojis = {animojis.PEPE_JAM, animojis.HACKERMANS, animojis.GAMBAGE, animojis.HYPERS}

    def __init__(self, allowed_player_ids: Set[str], bot, button_style, round_name):
        super().__init__(allowed_player_ids, bot, button_style, round_name)

    def get_embed(self, end_time: int) -> Embed:
        embed = discord.Embed(
            title=f"{animojis.BONGO_PEPE} {self.round_name} {animojis.BONGO_PEPE}",
            description="The least chosen emoji will lead you to the next game."
            "If only one emoji is chosen, 75% of you will be randomly eliminated",
            color=0x0052FB,
        )
        embed.add_field(name="Choice Deadline", value=f"<t:{end_time}:R>")
        return embed

    def get_winner_ids(self, color_counts: Counter) -> Tuple[Optional[Set[str]], Embed]:
        winner_ids = set()
        if not color_counts:
            embed = discord.Embed(
                title=f"{animojis.DEADGE} Nobody played in time {animojis.DEADGE}",
                description=f"No winners",
                color=0x0052FB,
            )

        elif len(color_counts) == 1:
            color1, count = color_counts.popitem()
            amount_players = count
            winner_ids = random.sample(
                self.color_choice_per_user_id.keys(), max(1, int(0.25 * amount_players))
            )
            embed = discord.Embed(
                title=f"{animojis.PEEPO_RIOT} Time is up {animojis.PEEPO_RIOT}",
                description=f"Everybody chose {color1}, I will randomly eliminate 75% of you.",
                color=0x0052FB,
            )

        else:
            winning_emoji = color_counts.most_common()[-1][0]
            winner_ids = {
                user_id
                for user_id, emoji in self.color_choice_per_user_id.items()
                if emoji == winning_emoji
            }
            embed = discord.Embed(
                title=f"{animojis.PEEPO_RIOT} Time is up {animojis.PEEPO_RIOT}",
                description=f"Winning emoji is: {winning_emoji}",
                color=0x0052FB,
            )
        return winner_ids, embed


class TwoLeastChosenLoose(ColorGameRound):
    emojis = {animojis.PEPE_JAM, animojis.HACKERMANS, animojis.GAMBAGE, animojis.HYPERS}

    def __init__(self, allowed_player_ids: Set[str], bot, button_style, round_name):
        super().__init__(allowed_player_ids, bot, button_style, round_name)

    def get_embed(self, end_time: int) -> Embed:
        embed = discord.Embed(
            title=f"{animojis.BONGO_PEPE} {self.round_name} {animojis.BONGO_PEPE}",
            description="The two least chosen emojis will lead you to **loose** this round."
            " If only two or less emojis are chosen, 75% of you will be randomly eliminated",
            color=0x0052FB,
        )
        embed.add_field(name="Choice Deadline", value=f"<t:{end_time}:R>")
        return embed

    def get_winner_ids(self, color_counts: Counter) -> Tuple[Optional[Set[str]], Embed]:
        winner_ids = set()
        if not color_counts:
            embed = discord.Embed(
                title=f"{animojis.DEADGE} Nobody played in time {animojis.DEADGE}",
                description=f"No winners",
                color=0x0052FB,
            )

        elif len(color_counts) == 1:
            color1, amount_players = color_counts.popitem()
            winner_ids = random.sample(
                self.color_choice_per_user_id.keys(), max(1, int(0.25 * amount_players))
            )
            embed = discord.Embed(
                title=f"{animojis.PEEPO_RIOT} Time is up {animojis.PEEPO_RIOT}",
                description=f"Everybody chose {color1}, I will randomly eliminate 75% of you",
                color=0x0052FB,
            )

        elif len(color_counts) == 2:
            color1, color2 = color_counts.most_common(2)
            amount_players = color1[1] + color2[1]
            amount_of_winners = max(1, int(0.25 * amount_players))
            winner_ids = random.sample(
                self.color_choice_per_user_id.keys(), amount_of_winners
            )
            embed = discord.Embed(
                title=f"{animojis.PEEPO_RIOT} Time is up {animojis.PEEPO_RIOT}",
                description=f"{color1[0]} and {color2[0]} were the ony two chosen emojis {animojis.SCAM},"
                f" I will randomly eliminate 75% of you.",
                color=0x0052FB,
            )

        else:
            color1, color2 = color_counts.most_common()[-2:]
            winner_ids = {
                user_id
                for user_id, color in self.color_choice_per_user_id.items()
                if color != color1[0] and color != color2[0]
            }
            embed = discord.Embed(
                title=f"{animojis.PEEPO_RIOT} Time is up {animojis.PEEPO_RIOT}",
                description=f"Winning emojis are: {color1[0]}  and {color2[0]}",
                color=0x0052FB,
            )
        return winner_ids, embed
