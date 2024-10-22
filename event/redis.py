from core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, scoped_session
import redis
import asyncio

engine = create_async_engine(
    settings.mysql.db_url,  # 数据库URL
    pool_size=5,  # 连接池的大小，默认为 5
    max_overflow=10,  # 连接池满时允许的最大溢出连接数，默认为 10
    pool_timeout=30,  # 等待连接的超时时间（秒）
    pool_recycle=3600  # 多长时间回收连接，防止超时，单位秒
)

# 创建一个 `Session` 类
Session = async_scoped_session(sessionmaker(bind=engine, class_ = AsyncSession), scopefunc=asyncio.current_task)

pool = redis.ConnectionPool.from_url(settings.redis.url)
