from typing import Any, Dict, Generic, Iterable, Iterator, List, Sequence, Tuple, TypeVar, Union
import discord
import random
import collections

T = TypeVar("T")
LikeList = Union[List[T], T]

def flat_list(l:LikeList[T])->List[Any]:
    def fn(l):
        for el in l:
            if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
                yield from fn(el)
            else:
                yield el
    return [x for x in fn([l])]


def pick_random(value: List[T]) -> T:
    return random.choice(value)

class RoomTemplate:
    type: str
    name: List[str]

    def __init__(self, obj: Dict[str, Any]) -> None:
        self.type = obj["type"]
        self.name = flat_list(obj["name"])

    async def create_room(self, category: discord.CategoryChannel) -> discord.abc.GuildChannel:
        if self.type == "voice":
            room = await category.create_voice_channel(name=pick_random(self.name))
        elif self.type == "text":
            room = await category.create_text_channel(name=pick_random(self.name))
        else:
            raise ValueError(f"room type '{self.type}' is invalid.")            
        return room

class CategoryTemplate:
    description: str
    alias: List[str]
    name: List[str]
    rooms: List[RoomTemplate]

    def __init__(self, obj: Dict[str, Any]) -> None:
        self.name = flat_list(obj["name"])
        self.description = obj.get("description") or ""
        self.alias = flat_list(obj.get("alias") or [])
        self.rooms = [RoomTemplate(data) for data in obj["rooms"]]

    async def create_category(self, guild: discord.Guild, roles: List[str]) -> Tuple[discord.CategoryChannel, List[discord.abc.GuildChannel]]:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }
        # 閲覧できるロールを設定
        for role in roles:
            overwrites[role] = discord.PermissionOverwrite(view_channel=True)

        category = await guild.create_category(pick_random(self.name))
        
        created_rooms = []
        
        for room in self.rooms:
            created_rooms.append(await room.create_room(category))

        print((category,created_rooms))

        return (category,created_rooms)