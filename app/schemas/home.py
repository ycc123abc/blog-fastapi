from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List
from typing import T

class Homelist(BaseModel, Generic[T]):
    items: List[T]

    @classmethod
    def create(cls,  items: List[T]):
        return cls(
            items=items
        )

class Usercard(BaseModel):
    username:str
    github:str
    views_num:int
    favor_num:int
    articles_num:int