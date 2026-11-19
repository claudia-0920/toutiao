from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud import users
from models.users import User
from schemas.users import UserRequest, UserResponse, UserInfoResponse, UserUpdateRequest, UpdatePasswordRequest
from utils import auth
from utils.auth import get_current_user
from utils.response import sussess_response

router = APIRouter(prefix="/api/user", tags=["users"])

@router.post("/register")
async def register(user_data : UserRequest, db: AsyncSession = Depends(get_db)):
    existing_user = await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    user = await users.create_user(db, user_data)
    token = await users.create_token(db,user.id)
    # return {
    #     "code": 200,
    #     "msg": "success",
    #     'data': {
    #         'token': token,
    #         'userinfo':{
    #             'id': user.id,
    #             "username": user_data.username,
    #             'bio':user.bio,
    #             'avatar':user.avatar,
    #         }
    #     }
    # }
    return sussess_response(msg = '注册成功',data = UserResponse(token= token,userInfo = UserInfoResponse.model_validate(user)))

@router.post("/login")
async def login(user_data : UserRequest, db: AsyncSession = Depends(get_db)):
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="用户名或密码错误")
    token = await users.create_token(db,user.id)
    return sussess_response(msg='登录成功',data = UserResponse(token= token,userInfo = UserInfoResponse.model_validate(user)))

@router.get("/info")
async def user_info(user_info:User = Depends(get_current_user) ):
    return sussess_response(msg='获取信息成功',data=UserInfoResponse.model_validate(user_info))

@router.put("/update")
async def user_update(user_data: UserUpdateRequest,user_info:User = Depends(get_current_user), db: AsyncSession = Depends(get_db) ):
    user = await users.update_user(db,user_info.username, user_data)
    return sussess_response(msg='修改用户信息成功',data=UserInfoResponse.model_validate(user))

@router.put("/password")
async def update_pwd(password_data:UpdatePasswordRequest,
                     user: User = Depends(get_current_user),
                     db:AsyncSession = Depends(get_db)):
    res_change_pwd = await users.change_password(db,password_data.old_password,password_data.new_password,user)
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='修改密码失败，请稍后再试')
    return sussess_response(msg='修改密码成功')
