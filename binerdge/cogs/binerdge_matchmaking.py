import discord
import logging
from typing import Optional, Dict
import random
from binerdge.static.bynaryge_embed_contents import bynaryge_rules, bynaryge_example
from utils.command_check import only_owners
from discord.ext import commands, tasks
from discord.ui import Button, View

class MatchMaking(commands.Cog):
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

    async def find_or_create_channel(self):
        matchmaking_channel = discord.utils.get(
            self.guild.channels, name=self.channel_name
        )
        if not matchmaking_channel:
            matchmaking_channel = await self.guild.create_text_channel(
                name=self.channel_name,
            )
        self.channel = matchmaking_channel

    def get_matchmaking_embed(self):
        embed_matchmaking = discord.Embed(
            title="Binerdge's Matchmaking",
            description=f"React with ✅ / ❎ to tag / untag yourself for a game! See the rules of the game below.",
            color=0xFFB500,
        )

        embed_matchmaking.add_field(
            name="Rules",
            value=bynaryge_rules,
            inline=False,
        )

        embed_matchmaking.add_field(
            name="Example",
            value=bynaryge_example,
            inline=False,
        )

        if self.sign_ups_queue:
            embed_matchmaking.add_field(
                name="Queued players",
                value=f"{' '.join([user.mention for user in self.sign_ups_queue.values()])}",
                inline=False,
            )
        else:
            embed_matchmaking.add_field(
                name="Queued players",
                value="Empty Queue",
                inline=False,
            )
        return embed_matchmaking

    def cog_unload(self):
        self.atomic_match.cancel()

    async def post_embed(self):
        embed_matchmaking = self.get_matchmaking_embed()
        self.message: discord.Message = await self.channel.send(embed=embed_matchmaking)
        await self.message.add_reaction("✅")
        await self.message.add_reaction("❎")

    async def update_matchmaking_embed(self):
        matchmaking_embed = self.get_matchmaking_embed()
        await self.message.edit(embed=matchmaking_embed)

    async def create_match(self, member_1: discord.Member, member_2: discord.Member):
        match_handler = self.bot.get_cog("MatchHandler")
        await match_handler.create_match(
            member_1=member_1, member_2=member_2, guild=self.guild
        )

    @tasks.loop(seconds=60*3)
    async def atomic_match(self):
        while len(self.sign_ups_queue) >= 2:
            user_ids = random.sample(self.sign_ups_queue.keys(), 2)
            self.logger.info(f"Creating Binerdge Match with users {user_ids}")
            await self.create_match(
                member_1=self.sign_ups_queue.pop(user_ids[0]),
                member_2=self.sign_ups_queue.pop(user_ids[1]),
            )
            await self.update_matchmaking_embed()

    @commands.check(only_owners)
    @commands.command()
    async def start_binerdge_matchmaking(self, ctx):
        guild = ctx.guild
        self.guild = guild
        await self.find_or_create_channel()
        await self.channel.purge(limit=200)
        await self.post_embed()
        self.atomic_match.start()
        await ctx.message.delete()
        while True:
            def check(reaction, ctx):
                return (
                    (not ctx.bot)
                    and str(reaction.emoji) in {"✅", "❎"}
                    and reaction.message == self.message
                )
            reaction, member = await self.bot.wait_for("reaction_add", check=check)
            if reaction.emoji == "✅":
                self.sign_ups_queue[member.id] = member
            else:
                self.sign_ups_queue.pop(member.id, None)
            await self.update_matchmaking_embed()
            await reaction.remove(member)

    # @commands.check(only_owners)
    # @commands.command()
    # async def select(self, ctx):
    #     await ctx.send(
    #         "Queue for Bynerdge!",
    #         components=[
    #             Select(
    #                 placeholder="kekw",
    #                 options=[
    #                     SelectOption(label="Queue", value="a"),
    #                     SelectOption(label="Cancel", value="b"),
    #                 ],
    #                 custom_id="select1",
    #             )
    #         ],
    #     )
    #
    #     interaction = await self.bot.wait_for(
    #         "select_option", check=lambda inter: inter.custom_id == "select1"
    #     )
    #     await interaction.send(content=f"{interaction.values[0]} selected!")
    #
    # @commands.check(only_owners)
    # @commands.command()
    # async def button(self, ctx):
    #     await ctx.send("Buttons!", components=[Button(label="Button", custom_id="button1")])
    #     interaction = await self.bot.wait_for(
    #         "button_click", check=lambda inter: inter.custom_id == "button1"
    #     )
    #     await interaction.send(content="Button Clicked")

    @commands.check(only_owners)
    @commands.command()
    async def color_game(self, ctx):
        players_per_color = {}
        green_button = Button(
            label="Green",
            style=discord.ButtonStyle.green,
            emoji="<a:PepegeClap:932346473922834552>",
        )
        red_button = Button(
            label="Red",
            style=discord.ButtonStyle.red,
            emoji="<a:PepegeClap:932346473922834552>",
        )

        async def button_callback(interaction: discord.Interaction):
            print(interaction)

        green_button.callback = button_callback
        red_button.callback = button_callback
        view = View()
        view.add_item(green_button)
        view.add_item(red_button)

        await ctx.send("Choose wisely your color", view=view)
