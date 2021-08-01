from typing import Any, Dict, Generic, List, Sequence, TypeVar, Union
import discord

T = TypeVar("T")
LikeList = Union[List[T], T]


def flat_list(value: LikeList[T]) -> List[T]:
    if isinstance(value, list):
        return value
    else:
        return [value]


def pick_random(value: List[T]) -> T:


class RoomTemplate:
    type: str
    name: str

    def __init__(self, obj: Dict[str, Any]) -> None:
        self.type = obj["type"]
        self.name = obj["type"]


class ChannelTemplate:
    description: str
    alias: List[str]
    name: List[str]
    rooms: List[RoomTemplate]

    def __init__(self, obj: Dict[str, Any]) -> None:
        self.description = obj["description"]
        self.alias = flat_list(obj["alias"])
        self.rooms = [RoomTemplate(data) for data in flat_list(obj["rooms"])]

    async def createChannel(self, guild: discord.Guild):
        guild.
