from anyio import Path
from fastapi import UploadFile
from fastapi.staticfiles import StaticFiles
import os
import shutil
async def file_work(file_:UploadFile,MEDIA_URL="cover",base_root="app/static"):
    filename=file_.filename
    filename=os.path.join(os.path.join(base_root,MEDIA_URL),filename)
    with open(filename,"wb") as f:
        shutil.copyfileobj(file_.file, f)  # 
