from abc import ABC, abstractmethod
from discord import Member, Message, TextChannel, Embed
from typing import Optional, Type
from datetime import datetime
from src.game_apis import GameAPI
from pydantic import BaseModel


class Duel(ABC):
    game_name: str
    GameAPI: Type[GameAPI]

    def __init__(
            self,
            member_1: Member,
            member_2: Member,
            # transform into private thread later
            channel: TextChannel,
            message: Message,
            winner: Optional[Member],
            start_date: datetime,
            last_update: datetime,
            ongoing: bool
    ):
        self.member_1 = member_1
        self.member_2 = member_2
        self.channel = channel
        self.message = message
        self.winner = winner
        self.start_date = start_date
        self.last_update = last_update
        self.ongoing = ongoing

    @abstractmethod
    def to_pydantic_schema(self) -> Type[BaseModel]:
        pass

    @abstractmethod
    def check_play(self, *args) -> bool:
        ...

    @abstractmethod
    def process_play(self, *args) -> bool:
        ...

    @abstractmethod
    async def is_finished(self) -> bool:
        ...

    @abstractmethod
    async def terminate(self) -> None:
        ...

    @abstractmethod
    def get_duel_embed(self) -> Embed:
        ...

    async def update_embed_match(self):
        updated_embed = self.get_duel_embed()
        await self.message.edit(embed=updated_embed)

    def update_current_player(self) -> None:
        if self.member_1 == self.current_player:
            self.current_player = self.member_2
        else:
            self.current_player = self.member_1

