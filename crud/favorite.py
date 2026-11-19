from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.favorite import Favorite
from models.news import news


async def is_news_favorite(db:AsyncSession,user_id:int, news_id:int):
    stmt = select(Favorite).where(Favorite.user_id == user_id,Favorite.news_id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None

async def add_favorite(db:AsyncSession,user_id:int, news_id:int):
    favorite = Favorite(user_id=user_id,news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

async def remove_favorite(db:AsyncSession,user_id:int, news_id:int):
    stmt = delete(Favorite).where(Favorite.user_id == user_id,Favorite.news_id == news_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0

async def get_favorite_list(db:AsyncSession,user_id:int,page:int,page_size:int):
    query_count = select(func.count(Favorite)).where(Favorite.user_id == user_id)
    query_result = await db.execute(query_count)
    total = query_result.scalar_one_or_none()
    offset = (page-1)*page_size
    query_list = (select(news,Favorite.created_at.label('favorite_time'),Favorite.id.label('favorite_id')).
                     join(Favorite,Favorite.news_id == news.id).
                     where(Favorite.user_id == user_id).
                     order_by(Favorite.created_at.desc()).
                     offset(offset).limit(page_size))
    db_favorite_list = await db.execute(query_list)
    result_list = db_favorite_list.all()
    return result_list,total

async def clear_favorite(user_id:int,db:AsyncSession):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0
