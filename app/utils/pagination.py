from tortoise.queryset import QuerySet
from app.schemas.pagination import PaginationParams


async def paginate(query: QuerySet, params: PaginationParams,count:int) -> tuple:
    """执行分页查询并返回结果和总数"""
    offset = (params.page - 1) * params.size

    return (
        await query.offset(offset).limit(params.size),
        await count
    )