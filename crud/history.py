from datetime import datetime
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.history import History
from models.news import news


async def add_history(db:AsyncSession,user_id:int,news_id:int):
    query = select(History).where(History.user_id == user_id,History.news_id == news_id)
    result = await db.execute(query)
    existing_history = result.scalar_one_or_none()
    if existing_history:
        existing_history.view_time = datetime.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history
    else:
        history = History(user_id=user_id, news_id=news_id)
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history

async def get_history_list(db:AsyncSession,user_id:int,page:int=1,page_size:int=10):
    count = select(func.count(History.id)).where(History.user_id==user_id)
    db_count = await db.execute(count)
    total = db_count.scalar_one()
    offset = (page - 1) * page_size
    stmt = (select(news,History.view_time.label('view_time'),History.id.label('history_id')).
            join(History,History.news_id==news.id).
             where(History.user_id == user_id).
             order_by(History.view_time.desc()).
             offset(offset).limit(page_size))
    db_history = await db.execute(stmt)
    histories = db_history.all()
    return histories,total

async def delete_one(db:AsyncSession,user_id:int,news_id:int):
    stmt = delete(History).where(History.news_id == news_id,History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount>0

async def clear_history(db:AsyncSession,user_id:int):
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0
    
