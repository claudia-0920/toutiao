from fastapi import Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud import users


async def get_current_user(
        authorization:str = Header(...,alias='Authorization'),
        db: AsyncSession = Depends(get_db)):
    # Bearer xxxxx
    # token = authorization.split(" ")[1]
    token = authorization.replace("Bearer ", "")
    user_info = await users.get_user_by_token(db, token)
    if not user_info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,)
    return user_info