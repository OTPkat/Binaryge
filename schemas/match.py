import datetime

import discord
import datetime
from typing import Optional

class Match:
    def __init__(
        self,
        channel: discord.TextChannel,
        message: discord.Message,
        member_1: discord.Member,
        member_2: discord.Member,
        n: int,
        current_sum: int,
        start_date: datetime.datetime,
        last_update: datetime.datetime,
        current_player: Optional[discord.Member] = None,
    ):
        self.channel = channel
        self.message = message
        self.member_1 = member_1
        self.member_2 = member_2
        self.n = n
        self.current_sum = current_sum
        self.start_date = start_date
        self.last_update = last_update
        self.current_player = current_player

    def check_addition(self, submitted_binary_number: str):
        return int(submitted_binary_number, 2) + self.current_sum <= 2*self.n

    def add(self, submitted_binary_number: str):
        self.current_sum += int(submitted_binary_number, 2)

    def update_current_player(self):
        if self.member_1 == self.current_player:
            self.current_player = self.member_2
        else:
            self.current_player = self.member_1
