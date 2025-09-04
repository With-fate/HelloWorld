import os


class Config:
    # MySQL数据库配置
    MYSQL_HOST = 'localhost'  # MySQL服务器地址
    MYSQL_PORT = 3307  # MySQL端口
    MYSQL_USER = 'root'  # MySQL用户名
    MYSQL_PASSWORD = 'root'  # MySQL密码
    MYSQL_DB = 'helloworld'  # 数据库名称
    MYSQL_CHARSET = 'utf8mb4'

    # 构建SQLAlchemy连接字符串
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset={MYSQL_CHARSET}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key-change-in-production'