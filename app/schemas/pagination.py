from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from typing import Generic, TypeVar, List
T = TypeVar('T')
# 分页参数
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")

# 分页响应
class PaginatedResponse(GenericModel, Generic[T]):
    total: int
    page: int
    size: int
    total_pages: int
    items: List[T]

    @classmethod
    def create(cls, total: int, items: List[T], params: PaginationParams):
        total_pages = (total + params.size - 1) // params.size
        return cls(
            total=total,
            page=params.page,
            size=params.size,
            total_pages=total_pages,
            items=items
        )