import asyncio
from abc import ABC, abstractmethod
from discord.ui import Button, View

import discord
from discord.ext import commands
from discord import Embed
from typing import Optional, Set, Dict
from collections import Counter


class ColorGameRound(ABC):
    round_name: str
    emojis_per_color: Dict[str, str]

    def __init__(self, allowed_player_ids: Set[str], bot: commands.Bot):
        self.allowed_player_ids = allowed_player_ids
        self.bot = bot

    @abstractmethod
    def solve_round(self, ctx) -> Set[int]:
        """
        :return: list of discord user id for next round
        """
        ...

    @abstractmethod
    def get_embed(self) -> Embed:
        ...

    @abstractmethod
    def get_view(self) -> View:
        ...

    @abstractmethod
    async def start_round(self, ctx):
        ...


class ColorGameFirstRound(ColorGameRound):
    round_name = "Follow them"
    emojis_per_color = {
        "Green": "<a:PepegeClap:932346473922834552>",
        "Gray": "<a:bongoLove:940379773752979467>",
        "Blurple": "<a:peepoRiot:933351979583930379>",
        "Red": "<a:bongoPepe:940379774474420294>"}

    def __init__(self, allowed_player_ids: Set[str], bot):
        super().__init__(allowed_player_ids, bot)
        self.color_choice_per_user_id: Optional[Dict[int, str]] = dict()

    def get_embed(self) -> Embed:
        embed = discord.Embed(
            title=f"Color Game - {self.round_name}",
            description=f"Anyone can enter at this stage, simply choose a color. If you reclick a color, that will"
                        f"simply update your choice.",
            color=0x0052FB,
        )

        embed.add_field(
            name="Rules",
            value="In this round players have to choose a color. "
                  "People having chosen one of the two most chosen colors will be eliminated."
                  "You have 5 minutes.",
            inline=False,
        )
        return embed

    def get_view(self) -> View:
        green_button = Button(
            label="Green",
            style=discord.ButtonStyle.green,
            emoji=self.emojis_per_color["Green"],
            custom_id="Green"
        )
        red_button = Button(
            label="Red",
            style=discord.ButtonStyle.red,
            emoji=self.emojis_per_color["Red"],
            custom_id="Red"
        )

        gray_button = Button(
            label="gray",
            style=discord.ButtonStyle.gray,
            emoji=self.emojis_per_color["Gray"],
            custom_id="Gray"
        )

        blurple_button = Button(
            label="blurple",
            style=discord.ButtonStyle.blurple,
            emoji=self.emojis_per_color["Blurple"],
            custom_id="Blurple"
        )

        async def button_callback(interaction: discord.Interaction):
            self.color_choice_per_user_id[interaction.user.id] = interaction.data["custom_id"]
            print(f"user {interaction.user.id} chose color: {interaction.data['custom_id']}")

        green_button.callback = button_callback
        red_button.callback = button_callback
        gray_button.callback = button_callback
        blurple_button.callback = button_callback

        view = View()
        view.add_item(green_button)
        view.add_item(red_button)
        view.add_item(gray_button)
        view.add_item(blurple_button)
        return view

    async def start_round(self, ctx):
        await ctx.send("`Let the game begin`", view=self.get_view(), embed=self.get_embed())
        await asyncio.sleep(15)
        await ctx.send("`30 seconds remaining`")
        await asyncio.sleep(15)
        await ctx.send("`Proceeding to elimination`")
        winner_ids = await self.solve_round(ctx=ctx)
        return winner_ids

    async def solve_round(self, ctx):
        if not self.color_choice_per_user_id:
            embed = discord.Embed(
                title=f"Nobody played in time",
                description=f"No winners",
                color=0x0052FB,
            )
            await ctx.send("`Recap: `", embed=embed)
            return {}
        print(f"Proceeding to solve round with following player choices : {self.color_choice_per_user_id}")
        color_counts = Counter(self.color_choice_per_user_id.values())
        try:
            color1, color2 = color_counts.most_common(2)
            winner_ids = {
                user_id for user_id, color in self.color_choice_per_user_id.items()
                if color == color1[0] or color == color2[0]
            }
            embed = discord.Embed(
                title=f"Time is up. Winning colors are:",
                description=f"{color1[0]} {self.emojis_per_color[color1[0]]} and {color2[0]} {self.emojis_per_color[color2[0]]}",
                color=0x0052FB,
            )
        except ValueError as e:
            color1 = color_counts.most_common(1)[0][0]
            winner_ids = {
                user_id for user_id, color in self.color_choice_per_user_id.items()
                if color == color1
            }
            embed = discord.Embed(
                title=f"Time is up. Winning color is:",
                description=f"{color1} {self.emojis_per_color[color1]}",
                color=0x0052FB,
            )

        winner_members = await asyncio.gather(*[self.bot.fetch_user(user_id) for user_id in winner_ids])
        embed.add_field(
            name="Players proceeding to the next round:",
            value=" ".join([x.mention for x in winner_members]),
            inline=False,
        )
        await ctx.send("`Recap: `", embed=embed)
        return winner_ids


class ColorGameSecondRound(ColorGameRound):
    round_name = "Hide out"
    emojis_per_color = {
        "Green": "<a:pepeJam:929537274293682226>",
        "Gray": "<a:HACKERMANS:929840112404148314> ",
        "Blurple": "<a:Gambage:938910418087325789> ",
        "Red": "<a:WeeHypers:935040370646057040> "}

    def __init__(self, allowed_player_ids: Set[str], bot):
        super().__init__(allowed_player_ids, bot)
        self.color_choice_per_user_id: Optional[Dict[int, str]] = dict()

    def get_embed(self) -> Embed:
        embed = discord.Embed(
            title=f"Color Game - {self.round_name}",
            description=f"Congratulations for making it to the second round.",
            color=0x0052FB,
        )

        embed.add_field(
            name="Rules",
            value="In this round players have to choose a color. "
                  "People having chosen one of the two least chosen colors will be eliminated."
                  "You have 5 minutes.",
            inline=False,
        )
        return embed

    def get_view(self) -> View:
        green_button = Button(
            label="Green",
            style=discord.ButtonStyle.green,
            emoji=self.emojis_per_color["Green"],
            custom_id="Green"
        )
        red_button = Button(
            label="Red",
            style=discord.ButtonStyle.red,
            emoji=self.emojis_per_color["Red"],
            custom_id="Red"
        )

        gray_button = Button(
            label="gray",
            style=discord.ButtonStyle.gray,
            emoji=self.emojis_per_color["Gray"],
            custom_id="Gray"
        )

        blurple_button = Button(
            label="blurple",
            style=discord.ButtonStyle.blurple,
            emoji=self.emojis_per_color["Blurple"],
            custom_id="Blurple"
        )

        async def button_callback(interaction: discord.Interaction):
            if interaction.user.id in self.allowed_player_ids:
                self.color_choice_per_user_id[interaction.user.id] = interaction.data["custom_id"]
                print(f"user {interaction.user.id} chose color: {interaction.data['custom_id']}")

        green_button.callback = button_callback
        red_button.callback = button_callback
        gray_button.callback = button_callback
        blurple_button.callback = button_callback

        view = View()
        view.add_item(green_button)
        view.add_item(red_button)
        view.add_item(gray_button)
        view.add_item(blurple_button)
        return view

    async def start_round(self, ctx):
        await ctx.send("`Let the game begin`", view=self.get_view(), embed=self.get_embed())
        await asyncio.sleep(15)
        await ctx.send("`30 seconds remaining`")
        await asyncio.sleep(15)
        await ctx.send("`Proceeding to elimination`")
        winner_ids = await self.solve_round(ctx=ctx)
        return winner_ids

    async def solve_round(self, ctx):
        if not self.color_choice_per_user_id:
            embed = discord.Embed(
                title=f"Nobody played in time",
                description=f"No winners",
                color=0x0052FB,
            )
            await ctx.send("`Recap: `", embed=embed)
            return {}
        print(f"Proceeding to solve round with following player choices : {self.color_choice_per_user_id}")
        color_counts = Counter(self.color_choice_per_user_id.values())
        try:
            color1, color2 = color_counts.most_common()[-2:]
            winner_ids = {
                user_id for user_id, color in self.color_choice_per_user_id.items()
                if color == color1[0] or color == color2[0]
            }
            embed = discord.Embed(
                title=f"Time is up. Winning colors are:",
                description=f"{color1[0]} {self.emojis_per_color[color1[0]]} and {color2[0]} {self.emojis_per_color[color2[0]]}",
                color=0x0052FB,
            )
        except ValueError as e:
            color1 = color_counts.most_common()[-1][0]
            winner_ids = {
                user_id for user_id, color in self.color_choice_per_user_id.items()
                if color == color1
            }
            embed = discord.Embed(
                title=f"Time is up. Winning color is:",
                description=f"{color1} {self.emojis_per_color[color1]}",
                color=0x0052FB,
            )

        winner_members = await asyncio.gather(*[self.bot.fetch_user(user_id) for user_id in winner_ids])
        embed.add_field(
            name="Players proceeding to the next round:",
            value=" ".join([x.mention for x in winner_members]),
            inline=False,
        )
        await ctx.send("`Recap: `", embed=embed)
        return winner_ids










