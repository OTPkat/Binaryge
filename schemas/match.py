import discord
import datetime
from typing import Optional, List
from src.utils import BinaryUtils


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
        amount_of_1_on_board: int,
        amount_of_0_on_board=int,
        current_player: Optional[discord.Member] = None,
        first_player: Optional[discord.Member] = None,
        winner: Optional[discord.Member] = None,
        plays: Optional[List[str]] = None
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
        self.first_player = first_player
        self.amount_of_0_on_board = amount_of_0_on_board
        self.amount_of_1_on_board = amount_of_1_on_board
        self.winner = winner
        self.plays = plays

    def check_addition(self, submitted_binary_number: str) -> bool:
        return (
            BinaryUtils.binary_string_to_int(submitted_binary_number) + self.current_sum
            <= 2 * self.n
        )

    def add(self, submitted_binary_number: str) -> None:
        self.amount_of_0_on_board += BinaryUtils.count_zeros_from_binary_string(
            submitted_binary_number
        )
        self.amount_of_1_on_board += BinaryUtils.count_ones_from_binary_string(
            submitted_binary_number
        )
        self.current_sum += BinaryUtils.binary_string_to_int(submitted_binary_number)
        self.plays.append(submitted_binary_number)

    def update_current_player(self) -> None:
        if self.member_1 == self.current_player:
            self.current_player = self.member_2
        else:
            self.current_player = self.member_1

    def is_next_player_blocked(self) -> bool:
        # this is checked after current player submit a move
        if self.current_sum == 2 * self.n - 1:
            if self.current_player == self.first_player:
                return not (self.amount_of_1_on_board % 2)
            else:
                return bool(self.amount_of_1_on_board % 2)
        else:
            return False

    def is_finished(self) -> bool:
        return (self.current_sum == 2 * self.n) or self.is_next_player_blocked()

    def format_plays_to_string(self):
        print(self.plays)
        return "```" + ' \n'.join(self.plays) + "```"

    def get_embed_from_match(self):
        description = f"The game is going on with n={self.n}={BinaryUtils.int_to_binary_string(self.n)}. \n Use `!bym answer` to submit your answer \n {self.current_player.mention} your turn!."
        embed_match = discord.Embed(
            title="Bynaryge's Match",
            description=description,
            color=0xffb500,
        )

        embed_match.add_field(
            name=f"Embed Numbers",
            value=self.format_plays_to_string(),
            inline=False,
        )

        embed_match.add_field(
            name=f"Amount of 1 written on the binary Board",
            value=f"```{self.amount_of_1_on_board}```",
            inline=False,
        )

        embed_match.add_field(
            name="Current sum",
            value=f"```{self.current_sum} = {BinaryUtils.int_to_binary_string(self.current_sum)}```",
            inline=False,
        )

        embed_match.add_field(
            name="Limit",
            value=f"```{2*self.n} = {BinaryUtils.int_to_binary_string(2*self.n)}```",
            inline=False,
        )
        return embed_match

    async def update_embed_match(self):
        updated_embed = self.get_embed_from_match()
        await self.message.edit(embed=updated_embed)
