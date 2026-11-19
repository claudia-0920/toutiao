
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import  AsyncSession
from models.news import category, news


async def get_categories(db:AsyncSession,skip:int,limit:int):
    stmt = select(category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_news_list(db:AsyncSession,category_id:int,skip:int=0,limit:int=10):
    stmt = select(news).where(news.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_count(db:AsyncSession,category_id:int):
    stmt = select(func.count(news.id)).where(news.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()

async def get_detail(db:AsyncSession,news_id:int):
    stmt = select(news).where(news.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def increase_view(db:AsyncSession,news_id:int):
    stmt = update(news).where(news.id == news_id).values(views = news.views + 1)
    result = await db.execute(stmt)
    await db.commit()
    # 更新 → 检查数据库是否真的命中了数据 → 命中了返回True
    return result.rowcount > 0

async def news_related(db:AsyncSession,category_id:int,news_id:int,limit:int=5):
    stmt = (select(news).where(news.category_id == category_id ,
                              news.id != news_id).
                            order_by(news.views.desc(),
                   news.publish_time.desc()).limit(limit))
    result = await db.execute(stmt)
    # return result.scalars().all()
    related_news = result.scalars().all()
    # 列表推导式 推导出新闻的核心数据，然后再 return
    return [{
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views
    } for news_detail in related_news]






