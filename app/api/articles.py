from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse

from pathlib import Path

from tortoise.transactions import in_transaction
import uuid
import os
from pathlib import Path
import re
from typing import List 
from app.models.models import Blog, Tag, BlogImage
from app.utils import file_work,apply_search,apply_pagination,apply_sort
from app.schemas import PaginationParams, PaginatedResponse,Homelist,ArticlePageParams
import datetime
from pydantic import BaseModel, field_serializer,validator
articlesrouter = APIRouter(prefix="/articles", tags=["articles"])

# 配置图片存储路径
MEDIA_DIR = Path("app/static/media")
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

@articlesrouter.post("/upload-markdown")  # 上传Markdown文章
async def upload_markdown_article(
    title: str = Form(...),
    category_id: str = Form(...),
    tag_ids: list[str] = Form(...),
    markdown_file: UploadFile = File(...),
    cover: UploadFile = File(...)
):
    # 读取Markdown内容
    markdown_content = await markdown_file.read()
    markdown_str = markdown_content.decode("utf-8")
    await file_work(cover)
    # 提取并处理图片
    updated_content, image_paths = await process_markdown_images(markdown_str)
    # 事务中创建文章和图片记录
    async with in_transaction():
        # 创建博客文章
        new_blog = await Blog.create(
            title=title,
            content=updated_content,
            favor=0,
            category_id=category_id,
            cover=cover.filename
        )
        user = await User.get(id=1)
        user.articles_num += 1
        await user.save()
        print(tag_ids)
        # 添加标签关联
        tags = await Tag.filter(id__in=tag_ids)
        await new_blog.tags.add(*tags)

        # 创建图片记录
        for img_path in image_paths:
            await BlogImage.create(
                blog_id=new_blog.id,
                image_path=img_path
            )

    return JSONResponse({
        "status": "success",
        "data": {
            "article_id": str(new_blog.id),
            "title": new_blog.title,
            "image_count": len(image_paths)
        }
    })

async def process_markdown_images(markdown_content):
    # 正则匹配Markdown图片语法 ![alt](path)
    img_pattern = re.compile(r"!\[([^]]*)\]\(([^)]+)\)")
    image_paths = []
    updated_content = markdown_content

    # 处理Base64图片或本地图片
    for match in img_pattern.findall(markdown_content):
        alt_text, img_src = match
        if img_src.startswith("data:image/"):
            # 处理Base64图片
            img_path = await save_base64_image(img_src)
            image_paths.append(img_path)
            # 更新Markdown中的图片路径
            updated_content = updated_content.replace(img_src, img_path)

    return updated_content, image_paths

async def save_base64_image(base64_str):
    # 解析Base64图片
    import base64

    # 提取图片格式和数据
    header, data = base64_str.split(",")
    img_format = header.split("/")[1].split("; ")[0]
    img_data = base64.b64decode(data)

    # 生成唯一文件名
    filename = f"{uuid.uuid4()}.{img_format}"
    file_path = MEDIA_DIR / filename

    # 保存图片
    with open(file_path, "wb") as f:
        f.write(img_data)

    # 返回可访问的URL路径
    return f"/media/{filename}"


@articlesrouter.get("/{article_id}")
async def get_article(article_id: str):
    # 查询文章并预加载关联数据
    article = await Blog.filter(id=article_id).prefetch_related(
        'category', 'tags', 'images'
    ).first()

    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # # 构建响应数据
    # return {
    #     "id": str(article.id),
    #     "title": article.title,
    #     "content": article.content,  # Markdown内容
    #     "favor": article.favor,
    #     "create_time": article.create_time.isoformat(),
    #     "update_time": article.update_time.isoformat(),
    #     "category": {
    #         "id": str(article.category.id),
    #         "name": article.category.name
    #     },
    #     "tags": [{
    #         "id": str(tag.id),
    #         "name": tag.name
    #     } for tag in article.tags],
    #     "images": [{
    #         "id": str(img.id),
    #         "image_path": img.image_path,
    #         "description": img.description
    #     } for img in article.images]
    # }





# 响应模型
class ItemOut(BaseModel):
    id: uuid.UUID
    title: str
    favor: int=0
    create_time: datetime.datetime = None
    update_time: datetime.datetime = None
    tags: List[str] = [] 
    cover: str = None
    views: int = 0

    @field_serializer('create_time', 'update_time')
    def serialize_dt(self, dt: datetime.datetime, _info):
        
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%d %H:%M:%S")


    @validator('tags', pre=True)
    def convert_category_to_name(cls, v):
            return [v_.name for v_ in v] if v else []


@articlesrouter.get("/homelist/", response_model=Homelist[ItemOut])
async def get_article_list():
    query = await Blog.all().prefetch_related("tags").offset(0).limit(5)
    return Homelist.create(query)


@articlesrouter.get("", response_model=PaginatedResponse[ItemOut])
async def get_article_list(params: ArticlePageParams = Depends()):
    # 1. 构建基础查询
    base_query = Blog.all().prefetch_related('tags')
    print(params.search_fields)
    # 2. 应用搜索条件
    search_query = await apply_search(
        query=base_query,
        search_term=params.search,
        search_fields=params.search_fields.split(",")    #["title", "tags__name"]
    )
    
    # 3. 应用排序
    sorted_query = apply_sort(
        query=search_query,
        sort_field="create_time",
        sort_direction=params.sort
    )
    
    # 4. 应用分页
    paginated_data, total = await apply_pagination(
        query=sorted_query,
        page=params.page,
        size=params.size
    )
    
    # 5. 返回分页响应
    return PaginatedResponse.create(total, paginated_data, params)





