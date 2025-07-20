from fastapi import APIRouter, Form,HTTPException
from fastapi.responses import JSONResponse
from app.models import User
from app.schemas import Usercard

introducerouter = APIRouter(prefix="/tags", tags=["tags"])

@introducerouter.get("/user-card")
async def user_card():
    user = await User.get(id=1)

    user_card = Usercard.create(
        username=user.username,
        github=user.github,
        articles=user.articles_num,
        favor=user.favor_num,
        views_num=user.views_num
    )