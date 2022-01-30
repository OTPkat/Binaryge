import discord
from datetime import datetime
from typing import Optional, List
from utils.binary import BinaryUtils
from src.abstract_duel import Duel
from src.game_apis import BinerdgeApi
from schemas.binerdge_duel import BinerdgeDuelSchema


class BinerdgeDuel(Duel):
    game_name = "Binerdge"
    game_api: BinerdgeApi

    def __init__(
        self,
        channel: discord.TextChannel,
        message: discord.Message,
        member_1: discord.Member,
        member_2: discord.Member,
        ongoing: bool,
        n: int,
        current_sum: int,
        start_date: datetime,
        last_update: datetime,
        amount_of_1_on_board: int,
        amount_of_0_on_board=int,
        current_player: Optional[discord.Member] = None,
        first_player: Optional[discord.Member] = None,
        winner: Optional[discord.Member] = None,
        plays: Optional[List[str]] = None

    ):
        super().__init__(
            channel=channel,
            message=message,
            member_1=member_1,
            member_2=member_2,
            start_date=start_date,
            last_update=last_update,
            ongoing=ongoing,
            winner=winner,
        )

        # Binerdge specific variables
        self.n = n
        self.current_player = current_player
        self.current_sum = current_sum
        self.first_player = first_player
        self.amount_of_0_on_board = amount_of_0_on_board
        self.amount_of_1_on_board = amount_of_1_on_board
        self.winner = winner
        self.plays = plays
        self.current_turn_message: Optional[discord.Message] = None

    def to_pydantic_schema(self) -> BinerdgeDuelSchema:
        return BinerdgeDuelSchema(
            channel_id=self.channel.id,
            message_id=self.message.id,
            member_1_id=self.member_1.id,
            member_2_id=self.member_2.id,
            ongoing=self.ongoing,
            n=self.n,
            start_date=self.start_date,
            last_update=self.last_update,
            winner_discord_user_id=self.winner.id,
            first_player_id=self.first_player.id
        )

    def check_play(self, submitted_binary_number: str) -> bool:
        return (
            BinaryUtils.binary_string_to_int(submitted_binary_number) + self.current_sum
            <= 2 * self.n
        )

    def process_play(self, submitted_binary_number: str) -> None:
        self.amount_of_0_on_board += BinaryUtils.count_zeros_from_binary_string(
            submitted_binary_number
        )
        self.amount_of_1_on_board += BinaryUtils.count_ones_from_binary_string(
            submitted_binary_number
        )
        self.current_sum += BinaryUtils.binary_string_to_int(submitted_binary_number)
        self.plays.append(submitted_binary_number)

    def is_next_player_blocked(self) -> bool:
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
        return "```" + ' \n'.join(self.plays) + "```"

    def get_duel_embed(self):
        description = f"The game is going on with `n={self.n}={BinaryUtils.int_to_binary_string(self.n)}`." \
                      f" \n Use `!bym binary_number` to submit your number \n {self.current_player.mention} your turn!."
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
            name=f"Amount of 1 in Embed Numbers",
            value=f"```{self.amount_of_1_on_board}```",
            inline=False,
        )

        embed_match.add_field(
            name="Current sum",
            value=f"```{self.current_sum} = {BinaryUtils.int_to_binary_string(self.current_sum)}```",
            inline=False,
        )

        embed_match.add_field(
            name="Sum Limit",
            value=f"```{2*self.n} = {BinaryUtils.int_to_binary_string(2*self.n)}```",
            inline=False,
        )
        return embed_match

    def terminate(self):
        pass

