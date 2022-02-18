from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class BinerdgeDuelSchema(BaseModel):
    id: Optional[int]
    channel_id: str
    message_id: str
    member_1_id: str
    member_2_id: str
    ongoing: bool
    n: int
    start_date: datetime
    last_update: datetime
    winner_discord_user_id: str
    first_player__id: str