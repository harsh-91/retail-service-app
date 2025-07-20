from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from core.auth_utils import get_current_user
from db.mongo import get_users_collection
from app.models.user import UserProfile

router = APIRouter(prefix="/users")


@router.get("/users", response_model=List[UserProfile])
def list_users(
    skip: int = Query(0, ge=0, description="How many users to skip"),
    limit: int = Query(10, le=100, description="Maximum users to return (max 100)"),
    current_user: dict = Depends(get_current_user)
):
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Admins only")
    
    users = get_users_collection()
    docs = users.find().skip(skip).limit(limit)
    results = []

    for user in docs:
        user.pop("_id", None)  # Remove Mongo ObjectId before returning
        results.append(user)
    
    return results
