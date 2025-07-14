import dotenv 
import os 

dotenv.load_dotenv()
print(os.getenv("POSTGRESQL_HOST"))
TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',  # asyncpg是PostgreSQL的驱动
            'credentials': {
                'host': os.getenv("POSTGRESQL_HOST"),  # 数据库的主机IP
                'port': 5432,  # 数据库主机端口
                'user': os.getenv("POSTGRESQL_USER"),  # 用户名
                'password': os.getenv("POSTGRESQL_PASSWORD"),  # 密码
                'database': os.getenv("POSTGRESQL_DB"),  # 数据库名称
                'minsize': 1,
                'maxsize': 3,
            }
        }
    },
    'apps': {
        'models': {
            'models': ['app.models.models', 'aerich.models'],  # 前是models.py文件的路径，后是迁移工具
            'default_connection': 'default',
        }
    },
    'use_tz': False,
    'timezone': 'Asia/Shanghai',
}
