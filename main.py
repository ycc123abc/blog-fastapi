import uvicorn
from fastapi import FastAPI, Request, Response
from tortoise.contrib.fastapi import register_tortoise
from fastapi.staticfiles import StaticFiles
from dependencies import TORTOISE_ORM  # 引入settings.py的配置
from  app.api import tagsrouter, articlesrouter
from fastapi.middleware.cors import CORSMiddleware
app_api = FastAPI(  # 自定义：api测试doc的标题
    title="PGuard API",
    description="PGuard 系统的 API 文档",
    version="1.0.0"
)
# Allow these methods to be used
methods = ["GET", "POST", "PUT", "DELETE"]

# Only these headers are allowed
headers = ["Content-Type", "Authorization"]

app_api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app_api.mount("/static", StaticFiles(directory="app/static"), name="static")
app_api.include_router(tagsrouter)
app_api.include_router(articlesrouter)

origins = [
    "http://localhost",
    "https://localhost:3000",
    "https://tools.domain.com",
    "https://www.domain.com",
]


register_tortoise(
    app=app_api,  # FastAPI实例
    config=TORTOISE_ORM,  # settings配置的文件
)

if __name__ == '__main__':  # 主程序入口
    uvicorn.run(  # 默认就行，本地利用uvicorn生成api测试doc
        "main:app_api",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
