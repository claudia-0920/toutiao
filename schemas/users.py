from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserRequest(BaseModel):
    username: str
    password: str

class UserInfoBase(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50,description="昵称")
    avatar: Optional[str] = Field(None, max_length=255,description="头像URL")
    gender: Optional[str] = Field(None, max_length=10,description="性别")
    bio: Optional[str] = Field(None, max_length=500,description="个人简介")

class UserInfoResponse(UserInfoBase):
    id: int
    username: str
    # 模型类配置
    model_config = ConfigDict(
        from_attributes=True,  # 允许从orm对象属性中取值
    )


class UserResponse(BaseModel):
    token: str
    userInfo : UserInfoResponse = Field(...,alias="userInfo")

    # 模型类配置
    model_config = ConfigDict(
        populate_by_name=True, # alais/字段名兼容
        from_attributes=True, # 允许从orm对象属性中取值
    )

class UserUpdateRequest(BaseModel):
    nickname: str = None
    avatar: str = None
    gender: str = None
    bio: str = None
    phone : str = None

class UpdatePasswordRequest(BaseModel):
    old_password: str = Field(...,alias="oldPassword")
    new_password: str = Field(...,min_length=6,alias="newPassword")