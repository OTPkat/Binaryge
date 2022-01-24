import discord


class Match:
    def __init__(
        self,
        channel: discord.TextChannel,
        message: discord.Message,
        member_1: discord.Member,
        member_2: discord.Member,
    ):
        self.channel = channel
        self.message = message
        self.member_1 = member_1
        self.member_2 = member_2