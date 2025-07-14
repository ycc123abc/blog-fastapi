from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import sys
from pathlib import Path

from tortoise.transactions import in_transaction
import uuid
import os
from pathlib import Path
import re
# sys.path.append(str(Path(__file__).parent.parent.parent))
from app.models.models import Blog, Category, Tag, BlogImage
router = APIRouter(prefix="/articles", tags=["articles"])

# 配置图片存储路径
MEDIA_DIR = Path("app/static/media")
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload-markdown")  # 上传Markdown文章
async def upload_markdown_article(
    title: str = Form(...),
    category_id: str = Form(...),
    tag_ids: list[str] = Form(...),
    markdown_file: UploadFile = File(...)
):
    # 读取Markdown内容
    markdown_content = await markdown_file.read()
    markdown_str = markdown_content.decode("utf-8")

    # 提取并处理图片
    updated_content, image_paths = await process_markdown_images(markdown_str)

    # 事务中创建文章和图片记录
    async with in_transaction():
        # 创建博客文章
        new_blog = await Blog.create(
            title=title,
            content=updated_content,
            favor=0,
            category_id=category_id
        )

        # 添加标签关联
        await new_blog.tags.add(*tag_ids)

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