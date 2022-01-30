from typing import Generic, TypeVar, Type
from schemas.binerdge_duel import BinerdgeDuelSchema
from pydantic import BaseModel

S = TypeVar("S", bound=Type[BaseModel])

# todo fill with requests to cloud run and may need to be abstract soon.


class GameAPI(Generic[S]):
    # define all the requests to API's here since they just mostly depend on schema for most of them. Can always
    # add specifics in the child class. but for the classical ones no need (create update delete).
    def create_duel(self, s: S) -> S:
        pass

    def update_duel(self, id_: int) -> S:
        pass

    def delete_duel(self, id_: int) -> S:
        pass


BinerdgeApi = GameAPI[BinerdgeDuelSchema]