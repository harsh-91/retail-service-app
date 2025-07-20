from fastapi import APIRouter, Depends, HTTPException
from models.user import UserProfile, UserProfileUpdate
from core.auth_utils import get_current_user
from db.mongo import get_users_collection

router = APIRouter()

@router.get("/profile", response_model=UserProfile)
def get_profile(current_user: dict = Depends(get_current_user)):
    # current_user dict loaded from JWT by dependency
    return current_user

@router.patch("/profile", response_model=UserProfile)
def update_profile(
    update: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    users = get_users_collection()
    update_data = {}

    # Allow updating these fields (add or remove as needed)
    if update.full_name is not None:
        update_data["full_name"] = update.full_name
    if update.language_pref is not None:
        allowed_langs = {"en", "hi", "bn", "te", "ta"}
        if update.language_pref not in allowed_langs:
            raise HTTPException(status_code=400, detail="Unsupported language")
        update_data["language_pref"] = update.language_pref
    if update.device_model is not None:
        update_data["device_model"] = update.device_model
    if update.device_type is not None:
        update_data["device_type"] = update.device_type

    if not update_data:
        raise HTTPException(status_code=400, detail="No profile fields to update")

    result = users.update_one(
        {"username": current_user["username"]},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch and return the updated profile
    user = users.find_one({"username": current_user["username"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.pop("_id", None)  # Remove Mongo's internal ObjectId
    return UserProfile(**user)
