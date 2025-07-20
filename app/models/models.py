from tortoise.models import Model
from tortoise import fields
import uuid  # 自动生成uuid要用的
from .fields import ImageField
from tortoise.signals import pre_save
from passlib.context import CryptContext



class Category(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.TextField()
    create_time=fields.DatetimeField(auto_now_add=True)
    update_time=fields.DatetimeField(auto_now=True)

class Tag(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.TextField()
    create_time=fields.DatetimeField(auto_now_add=True)
    update_time=fields.DatetimeField(auto_now=True)



    
class Blog(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    cover=fields.TextField()
    title = fields.TextField()
    content=fields.TextField()
    favor=fields.IntField()
    views=fields.IntField()
    create_time=fields.DatetimeField(auto_now_add=True)
    update_time=fields.DatetimeField(auto_now=True)
    category=fields.ForeignKeyField('models.Category',related_name='blogs')
    tags=fields.ManyToManyField('models.Tag',related_name='blogs')


# 添加图片模型
class BlogImage(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    blog = fields.ForeignKeyField('models.Blog', related_name='images')  # 关联到博客
    image_path = fields.TextField()  # 存储图片路径URL
    description = fields.TextField(null=True)  # 可选：图片描述
    upload_time = fields.DatetimeField(auto_now_add=True)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    articles_num=fields.IntField(default=0)
    favor_num=fields.IntField(default=0)
    views_num=fields.IntField(default=0)
    hashed_password = fields.CharField(max_length=128)
    github=fields.CharField(max_length=100, null=True)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        return pwd_context.hash(password)
    
    class Meta:
        table = "users"