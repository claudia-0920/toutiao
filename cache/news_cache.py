from typing import Dict, List, Any, Optional
from config.cache_conf import get_json_cache, set_cache


CATEGORY_KEY = "news:categories_key"
NEWS_LIST_PREFIX = "news_list:"
async def get_cache_categories():
    return await get_json_cache(CATEGORY_KEY)

async def set_cache_categories(data :List[Dict[str,Any]], expire:int=7200):
    return await set_cache(CATEGORY_KEY,data,expire)

# 写入列表缓存
async def set_cache_news_list(category_id:Optional[int],page:int,size:int,data:List[Dict[str,Any]],expire:int=1800):
    category_part = category_id if category_id is not None else "all"
    key = f'{NEWS_LIST_PREFIX}:{category_part}:{page}:{size}'
    return await set_cache(key,data,expire)

# 读取列表缓存
async def get_cache_news_list(category_id:Optional[int],page:int,size:int):
    category_part = category_id if category_id is not None else "all"
    key = f'{NEWS_LIST_PREFIX}:{category_part}:{page}:{size}'
    return await get_json_cache(key)