from pathlib import Path
import os
import uuid
from fastapi import UploadFile, HTTPException
from typing import Optional, Union, Any
from tortoise import fields
import re
import io

class ImageField(fields.Field):
    def __init__(
        self,
        upload_to: str = "uploads",
        max_length: int = 255,
        null: bool = False,
        **kwargs
    ):
        super().__init__(max_length=max_length, null=null, **kwargs)
        self.upload_to = upload_to
        self.static_dir = "app/static"  # 根据您的实际静态文件目录调整
        self.field_type = UploadFile

    def to_db_value(
        self, 
        value :Any, 
        instance: Any
    ) -> Optional[str]:
        """处理上传文件并返回存储路径"""
        if value is None:
            return None
        print(value.file.read())
        print(222222222222,value.headers)
        print(3333333333333,value)
        # 如果已经是字符串路径，直接返回
        if isinstance(value, str) and not value.startswith("UploadFile("):
            return value
            
        # 处理 UploadFile 对象或其字符串表示
        return self._handle_upload_file(value)

    def _handle_upload_file(self, value: Union[UploadFile, str]) -> str:
        """处理 UploadFile 对象或其字符串表示"""
        # 如果是字符串表示，转换为文件对象
        if isinstance(value, str) and value.startswith("UploadFile("):
            value = self._parse_uploadfile_str(value)
        
        # 验证文件类型
        if not value.content_type.startswith('image/'):
            raise HTTPException(400, "Invalid image format")
        
        # 创建存储目录
        upload_dir = Path(self.static_dir) / self.upload_to
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成唯一文件名
        ext = os.path.splitext(value.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = upload_dir / filename
        
        # 保存文件
        content = value.file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # 返回相对路径（相对于static目录）
        return f"/{self.upload_to}/{filename}"

    def _parse_uploadfile_str(self, value_str: str) -> UploadFile:
        """从字符串解析出 UploadFile 对象"""
        try:
            # 使用正则提取关键信息
            pattern = r"UploadFile\(filename='(.*?)', size=(\d+), headers=Headers\({(.*?)}\)\)"
            match = re.search(pattern, value_str)
            
            if not match:
                raise ValueError("Invalid UploadFile string format")
            
            filename = match.group(1)
            size = int(match.group(2))
            headers_str = match.group(3)
            
            # 解析 headers
            headers = {}
            header_pattern = r"'([^']+)': '([^']*)'"
            for header_match in re.finditer(header_pattern, headers_str):
                key = header_match.group(1)
                value = header_match.group(2)
                headers[key] = value
            
            # 创建文件对象
            file_obj = io.BytesIO(b"")  # 创建空文件对象
            file_obj.seek(0)
            
            # 创建 UploadFile 实例
            return UploadFile(
                filename=filename,
                file=file_obj,  # 使用空文件对象
                size=size,
                headers=headers
            )
        except Exception as e:
            raise ValueError(f"Failed to parse UploadFile string: {str(e)}") from e