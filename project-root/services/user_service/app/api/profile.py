from fastapi import APIRouter, Depends, HTTPException
from app.models.user import UserProfile, UserProfileUpdate
from app.core.auth_utils import get_current_user
from app.db.db import get_db

router = APIRouter()

@router.get("/profile", response_model=UserProfile)
def get_profile(current_user: dict = Depends(get_current_user)):
    # current_user dict loaded from JWT token by dependency
    return current_user

@router.patch("/profile", response_model=UserProfile)
def update_profile(update: UserProfileUpdate, current_user: dict = Depends(get_current_user)):
 with get_db() as conn:
    cursor = conn.cursor()
    # ...rest of your code...

    # Update fields as appropriate...
    cursor.execute(
        "UPDATE users SET full_name=?, language_pref=? WHERE id=?",
        (update.full_name or current_user["full_name"],
         update.language_pref or current_user["language_pref"],
         current_user["id"])
    )
    conn.commit()
    # Return updated user
    cursor.execute("SELECT username, email, full_name, language_pref FROM users WHERE id=?", (current_user["id"],))
    updated_user = cursor.fetchone()
    return {
        "username": updated_user[0],
        "email": updated_user[1],
        "full_name": updated_user[2],
        "language_pref": updated_user[3]
    }
