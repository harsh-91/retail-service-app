import bcrypt
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.db.mongo import get_users_collection  # USE THE MONGO HELPER NOW
from datetime import datetime, timedelta, UTC

SECRET_KEY = "supersecretkey"  # Use env in prod!
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, password_hash: str) -> bool:
    res = bcrypt.checkpw(password.encode(), password_hash.encode())
    print(f"Verifying password: {password} against hash: {password_hash} Result: {res}")
    return res

def create_access_token(data: dict, expires_minutes: int = 60):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=expires_minutes)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    users = get_users_collection()
    user = users.find_one({"username": username})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.pop("_id", None)  # Remove ObjectId for cleaner output (optional)
    return user
