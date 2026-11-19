from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker,AsyncSession

ASYNC_DB_URL = 'mysql+aiomysql://root:密码@localhost:3306/news_app?charset=utf8'
async_engine = create_async_engine(
    ASYNC_DB_URL,
    echo=True,
)
async_sessionLocal = async_sessionmaker(
    bind = async_engine,
    class_ = AsyncSession,
    expire_on_commit = False,
)

async def get_db():
    async with async_sessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
