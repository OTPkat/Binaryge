import discord
from discord.ext import commands, tasks
import logging
from typing import Optional, Dict
import random


class MatchMaking(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot,
        logger: logging.Logger,
        channel_name: str,
        category_name: str,
    ):
        self.bot = bot
        self.logger = logger
        self.message: Optional[discord.Message] = None
        self.sign_ups_queue: Optional[Dict[str, discord.User]] = {}
        self.channel_name = channel_name
        self.category_name = category_name
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
            title="Bynaryge's Matchmaking",
            description=f"React with ✅ to tag",
            color=0x00F0FF,
        )
        if self.sign_ups_queue:
            embed_matchmaking.add_field(
                name="Queued players for next batch:",
                value=f"{' '.join([user.mention for user in self.sign_ups_queue.values()])}",
                inline=False,
            )
        else:
            embed_matchmaking.add_field(
                name="Queued players for next batch:",
                value="Empty Queue",
                inline=False,
            )
        return embed_matchmaking

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

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info('yoyo')
        guilds = await self.bot.fetch_guilds(limit=2).flatten()
        for guild in guilds:
            self.guild = guild
            await self.find_or_create_channel()
            await self.post_embed()
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
            while len(self.sign_ups_queue) > 1:
                user_ids = random.sample(self.sign_ups_queue.keys(), 2)
                self.logger.info(f"Creating Binaryge Match with users {user_ids}")
                await self.create_match(
                    member_1=self.sign_ups_queue.pop(user_ids[0]),
                    member_2=self.sign_ups_queue.pop(user_ids[1]),
                )
