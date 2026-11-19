from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud import history
from models.users import User
from schemas.history import HistoryAddRequest, HistoryListResponse, HistoryNewsItemResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history",tags=["history"])

@router.post("/add")
async def add_history(data:HistoryAddRequest,
                      db:AsyncSession=Depends(get_db),
                      user:User=Depends(get_current_user),
                      ):
    result = await history.add_history(db,user.id,data.news_id)
    return success_response(msg='success',data=result)

@router.get("/list")
async def list_history(db:AsyncSession=Depends(get_db),
                       user:User=Depends(get_current_user),
                       page:int=Query(1,ge=1),
                       page_size:int=Query(10,ge=1,le=100,alias='pageSize')):
    histories,total = await history.get_history_list(db,user.id,page,page_size)
    history_list = [HistoryNewsItemResponse.model_validate({
        **news.__dict__,
        'viewTime':viewTime,
        "history_id": history_id
    })for news,viewTime,history_id in histories]
    hasmore = total > page * page_size
    data = HistoryListResponse(list=history_list,total = total,hasMore = hasmore)
    return success_response(data=data)

@router.delete("/delete/{news_id}")
async def delete_history(news_id:int,
                         db:AsyncSession=Depends(get_db),
                         user:User=Depends(get_current_user)):
    result = await history.delete_one(db,user.id,news_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='历史记录不存在')
    return success_response(msg='删除历史成功')

@router.delete("/clear")
async def clear_history(db:AsyncSession=Depends(get_db),
                        user:User=Depends(get_current_user)):
    count = await history.clear_history(db,user.id)
    return success_response(msg=f'清空{count}条历史记录')