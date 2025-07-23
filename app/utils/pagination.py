


from tortoise.queryset import QuerySet,Q
from app.schemas.pagination import PaginationParams

async def apply_search(query: QuerySet, search_term: str, search_fields: list) -> QuerySet:
    """
    应用搜索条件到查询集
    
    参数:
    - query: 原始查询集
    - search_term: 搜索关键词
    - search_fields: 要搜索的字段列表
    
    返回:
    应用搜索条件后的查询集
    """
    if not search_term or not search_fields:
        return query
    
    # 构建 OR 条件


    q_object = Q()
    for field in search_fields:
        print(field,search_fields)
        q_object |= Q(**{f"{field}__icontains": search_term})
    return query.filter(q_object)

def apply_sort(query: QuerySet, sort_field: str, sort_direction: str = "desc") -> QuerySet:
    """
    应用排序到查询集
    
    参数:
    - query: 原始查询集
    - sort_field: 排序字段
    - sort_direction: 排序方向 (asc/desc)
    
    返回:
    应用排序后的查询集
    """
    if not sort_field:
        return query
    
    if sort_direction == "asc":
        return query.order_by(sort_field)
    else:  # 默认降序
        return query.order_by(f"-{sort_field}")

async def apply_pagination(query: QuerySet, page: int, size: int) -> tuple:
    """
    应用分页到查询集
    
    参数:
    - query: 原始查询集
    - page: 当前页码
    - size: 每页大小
    
    返回:
    (分页数据, 总数)
    """
    offset = (page - 1) * size
    paginated_data = await query.offset(offset).limit(size)
    total = await query.count()
    return paginated_data, total