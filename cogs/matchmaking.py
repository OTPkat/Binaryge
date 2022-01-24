import discord
from discord.ext import commands, tasks
import logging
from typing import Optional, Dict


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
        self.matchmaking.start()

    def cog_unload(self):
        self.matchmaking.cancel()

    async def find_or_create_channel(self):
        matchmaking_channel = discord.utils.get(
            self.guild.channels, name=self.channel_name
        )
        if not matchmaking_channel:
            matchmaking_channel = await self.guild.create_text_channel(
                name=self.channel_name,
            )
        self.channel = matchmaking_channel

    async def get_matchmaking_embed(self):
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
        embed_matchmaking = discord.Embed(
            title="Bynaryge's Matchmaking",
            description=f"React with ✅ to tag",
            color=0x00F0FF,
        )
        embed_matchmaking.add_field(
            name="Queued players for next batch:",
            value=f"Empty Queue",
            inline=False,
        )
        self.message: discord.Message = await self.channel.send(embed=embed_matchmaking)
        await self.message.add_reaction("✅")
        await self.message.add_reaction("❎")

    async def update_matchmaking_embed(self):
        matchmaking_embed = await self.get_matchmaking_embed()
        await self.message.edit(embed=matchmaking_embed)

    @tasks.loop(seconds=60)
    async def matchmaking(self):
        pass

    async def await_sign_ups(self):
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

    @matchmaking.before_loop
    async def before_matchmaking(self):
        guilds = await self.bot.fetch_guilds(limit=2).flatten()
        for guild in guilds:
            self.guild = guild
            await self.find_or_create_channel()
            await self.post_embed()
            await self.await_sign_ups()
            break


def setup(bot):
    loader = bot.get_cog("Loader")
    bot.add_cog(
        MatchMaking(
            bot=bot,
            logger=loader.logger,
            category_name="binaryge",
            channel_name="bynaryge-matchmaking",
        )
    )
