from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from config.db_conf import get_db
from crud import favorite
from models.users import User
from schemas.favorite import FavoriteCheckResponse, FavoriteAddRequest, FavoriteListResponse
from utils.auth import get_current_user
from utils.response import sussess_response

router = APIRouter(prefix='/api/favorite',tags=['users'])

@router.get('/check')
async def favorite_check(news_id:int = Query(...,alias='newsId'),
                         user:User=Depends(get_current_user),
                         db:AsyncSession=Depends(get_db)):
    is_favorited=await favorite.is_news_favorite(db,user.id,news_id)
    return sussess_response(msg='检查收藏状态成功',data=FavoriteCheckResponse(isFavorite=is_favorited))

@router.post('/add')
async def favorite_add(data:FavoriteAddRequest,
                       db:AsyncSession=Depends(get_db),
                       user:User=Depends(get_current_user)):
    result = await favorite.add_favorite(db,user.id,data.news_id)
    return sussess_response(msg='添加收藏成功',data=result)

@router.delete('/remove')
async def favorite_remove(news_id:int=Query(...,alias='newsId'),
                          user:User=Depends(get_current_user),
                          db:AsyncSession=Depends(get_db)):
    result = await favorite.remove_favorite(db,user.id,news_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='此新闻未收藏')
    return sussess_response(msg='删除收藏成功')

@router.get('/list')
async def favorite_list(page:int=Query(1,ge=1),
                        page_size:int=Query(10,ge=10,le=100,alias='pageSize'),
                        user:User=Depends(get_current_user),
                        db:AsyncSession=Depends(get_db)):
    result_list,total = await favorite.get_favorite_list(db,user.id,page,page_size)
    favorite_list=[{
       **news.__dict__,
       "favorite.time":favorite_time,
        "favorite.id":favorite_id
    }
    for news,favorite_time,favorite_id in result_list]
    has_more = total > page * page_size
    data = FavoriteListResponse(list=favorite_list,total=total,hasMore=has_more)
    return sussess_response(msg='获取收藏列表成功',data=data)

@router.delete('/clear')
async def favorite_clear(user:User=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    count = await favorite.clear_favorite(user.id,db)
    return sussess_response(msg=f'清空{count}条收藏')