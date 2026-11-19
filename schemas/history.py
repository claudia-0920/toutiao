from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict
from schemas.base import NewsItemBase


class HistoryAddRequest(BaseModel):
    news_id: int = Field(...,alias='newsId')

class HistoryNewsItemResponse(NewsItemBase):
    history_id: int = Field(alias='historyId')
    viewtime:datetime = Field(alias='viewTime')
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class HistoryListResponse(BaseModel):
    list: List[HistoryNewsItemResponse]
    total: int
    hasmore: bool=Field(alias='hasMore')
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )