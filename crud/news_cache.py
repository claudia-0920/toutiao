from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import  AsyncSession

from cache.news_cache import get_cache_categories, set_cache_categories, get_cache_news_list, set_cache_news_list
from models.news import category, news
from schemas.base import NewsItemBase


async def get_categories(db:AsyncSession,skip:int,limit:int):
    cached_categories = await get_cache_categories()
    if cached_categories:
        return cached_categories
    stmt = select(category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()
    if categories:
        categories = jsonable_encoder(categories)
        await set_cache_categories(categories)
    return categories

async def get_news_list(db:AsyncSession,category_id:int,skip:int=0,limit:int=10):
    page = skip // limit + 1
    cached_news_list = await get_cache_news_list(category_id,page,limit)
    if cached_news_list:
        return [news(**item) for item in cached_news_list]
    stmt = select(news).where(news.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()
    # 写入缓存
    if news_list:
        news_data = [NewsItemBase.model_validate(item).model_dump(mode='json',by_alias=False) for item in news_list]
        await set_cache_news_list(category_id,page,limit,news_data)
    return news_list

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






