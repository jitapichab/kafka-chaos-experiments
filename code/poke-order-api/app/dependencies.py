from fastapi import Query
from typing import Optional


def get_user_id(user_id: str = Query(None)) -> Optional[int]:
    if user_id is None or not user_id:
        return None
    try:
        return int(user_id)
    except ValueError:
        return None
