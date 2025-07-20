from fastapi import APIRouter, Form,HTTPException
from fastapi.responses import JSONResponse



tagsrouter = APIRouter(prefix="/tags", tags=["tags"])

@tagsrouter.post("/")
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



