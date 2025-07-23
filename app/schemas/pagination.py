from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List
from typing import Optional,T
T = TypeVar('T')
# 分页参数
class PaginationParams(BaseModel):
    page: int = 1
    size: int = 10
    # search: Optional[str] = None
    # sort: Optional[str] = "desc"  # asc/desc

class ArticlePageParams(PaginationParams):
    search:  Optional[str] = None
    search_fields: str = "tag,stitle"
    sort: Optional[str] = "desc"


# 分页响应
class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    size: int
    total_pages: int
    items: List[T]

    @classmethod
    def create(cls, total: int, items: List[T], params: PaginationParams):
        total_pages = (total + params.size - 1) // params.size
        print(total_pages)
        return cls(
            total=total,
            page=params.page,
            size=params.size,
            total_pages=total_pages,
            items=items
        )