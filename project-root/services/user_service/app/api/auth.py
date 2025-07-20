from fastapi import APIRouter, HTTPException, Depends
from models.user import UserCreate, UserLogin, UserProfile, UserProfileUpdate
from core.auth_utils import hash_password, verify_password, create_access_token, get_current_user
from db.mongo import get_users_collection
from core.kafka_producer import emit_event

from datetime import datetime

router = APIRouter()

@router.post("/register")
def register(user: UserCreate):
    users = get_users_collection()

    # Enforce unique username and mobile; email is optional
    if users.find_one({"username": user.username}):
        raise HTTPException(status_code=409, detail="Username already exists")
    if users.find_one({"mobile": user.mobile}):
        raise HTTPException(status_code=409, detail="Mobile already used")
    if user.email and users.find_one({"email": user.email}):
        raise HTTPException(status_code=409, detail="Email already used")

    hashed_pwd = hash_password(user.password)
    user_doc = {
        "tenant_id": user.tenant_id,
        "username": user.username,
        "mobile": user.mobile,
        "email": user.email,
        "business_name": user.business_name,
        "password_hash": hashed_pwd,
        "full_name": user.full_name,
        "language_pref": user.language_pref,
        "device_model": user.device_model,
        "device_type": user.device_type,
        "roles": ["user"],
        "created_at": datetime.utcnow()
    }
    users.insert_one(user_doc)

    # Emit Kafka event after successful registration
    event = {
        "event_type": "user.registered",
        "tenant_id": user_doc["tenant_id"],
        "username": user_doc["username"],
        "mobile": user_doc["mobile"],
        "email": user_doc.get("email"),
        "full_name": user_doc.get("full_name"),
        "business_name": user_doc["business_name"],
        "device_model": user_doc.get("device_model"),
        "device_type": user_doc.get("device_type"),
        "registered_at": str(user_doc["created_at"])
    }
    emit_event("user.registered", event)

    return {"msg": "User registered"}

@router.post("/login")
def login(credentials: UserLogin):
    users = get_users_collection()
    query = {}
    if credentials.username:
        query["username"] = credentials.username
    elif credentials.mobile:
        query["mobile"] = credentials.mobile
    else:
        raise HTTPException(status_code=400, detail="username or mobile required for login")

    record = users.find_one(query)
    if not record or not verify_password(credentials.password, record["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": record["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", response_model=UserProfile)
def get_profile(current_user: dict = Depends(get_current_user)):
    return current_user

@router.patch("/profile", response_model=UserProfile)
def update_profile(update: UserProfileUpdate, current_user: dict = Depends(get_current_user)):
    users = get_users_collection()
    new_full_name = update.full_name or current_user.get("full_name")
    new_language = update.language_pref or current_user.get("language_pref")
    users.update_one(
        {"username": current_user["username"]},
        {"$set": {"full_name": new_full_name, "language_pref": new_language}}
    )
    user = users.find_one({"username": current_user["username"]})
    user.pop("_id", None)  # Optional: remove ObjectId before returning
    return {
        "username": user["username"],
        "mobile": user["mobile"],
        "Business_name": user["Business_name"],
        "email": user.get("email"),
        "full_name": user.get("full_name"),
        "language_pref": user.get("language_pref"),
        "device_model": user.get("device_model"),
        "device_type": user.get("device_type"),
        "roles": user.get("roles", [])
    }

@router.post("/change-password")
def change_password(old_password: str, new_password: str, current_user: dict = Depends(get_current_user)):
    users = get_users_collection()
    user = users.find_one({"username": current_user["username"]})
    if not user or not verify_password(old_password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Old password incorrect")
    new_hash = hash_password(new_password)
    users.update_one({"username": current_user["username"]}, {"$set": {"password_hash": new_hash}})
    return {"msg": "Password updated"}
