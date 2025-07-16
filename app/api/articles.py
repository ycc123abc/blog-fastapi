from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse

from pathlib import Path

from tortoise.transactions import in_transaction
import uuid
import os
from pathlib import Path
import re

from app.models.models import Blog, Category, Tag, BlogImage
from app.utils import file_work,paginate
from app.schemas import PaginationParams, PaginatedResponse

from pydantic import BaseModel
router = APIRouter(prefix="/articles", tags=["articles"])

# 配置图片存储路径
MEDIA_DIR = Path("app/static/media")
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload-markdown")  # 上传Markdown文章
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


@router.get("/{article_id}")
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

@router.post("/tags")
async def create_tag(name: str = Form(...)):
    print(name)
    # 检查标签是否已存在
    existing_tag = await Tag.filter(name=name).first()
    if existing_tag:
        raise HTTPException(status_code=400, detail="标签已存在")

    # 创建新标签
    new_tag = await Tag.create(name=name)

    return JSONResponse({
        "status": "success",
        "data": {
            "tag_id": str(new_tag.id),
            "name": new_tag.name,
            "create_time": new_tag.create_time.isoformat()
        }
    })



@router.post("/category")
async def create_category(name: str = Form(...)):
    print(name)
    # 检查目录是否已存在
    existing_category = await Category.filter(name=name).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="标签已存在")

    # 创建新标签
    new_category = await Category.create(name=name)

    return JSONResponse({
        "status": "success",
        "data": {
            "category_id": str(new_category.id),
            "name": new_category.name,
            "create_time": new_category.create_time.isoformat()
        }
    })



# 响应模型
class ItemOut(BaseModel):
    id: int
    title: str
    favor: int
    create_time: str = None
    update_time: str = None
    category_id: str = None
    cover: str = None

    class Config:
        orm_mode = True

@router.get("/list/",response_model=PaginatedResponse[ItemOut])
async def get_article_list(params: PaginationParams = Depends()):
    count = await Blog.all().count()
    query=await Blog.all().offset((params.page - 1) * params.size).limit(params.size)
    items, total = await paginate(query, params,count)
    return PaginatedResponse.create(total, items, params)

