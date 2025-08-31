"""
Аутентификация и авторизация
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt

from src.core.config import settings
from src.core.security import verify_password, get_password_hash

router = APIRouter()
security = HTTPBearer()

# Временное хранилище пользователей (в памяти)
users_db = {}

class UserCreate(BaseModel):
    """Модель для создания пользователя"""
    email: EmailStr
    password: str
    full_name: str
    role: str = "warehouse_keeper"

class UserLogin(BaseModel):
    """Модель для входа"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Модель ответа пользователя"""
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    """Модель токена"""
    access_token: str
    token_type: str
    expires_at: datetime
    user: UserResponse

class TokenData(BaseModel):
    """Данные токена"""
    email: Optional[str] = None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt, expire

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Проверка JWT токена"""
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

def get_user_by_email(email: str):
    """Получить пользователя по email"""
    for user_id, user_data in users_db.items():
        if user_data["email"] == email:
            return {
                "id": user_id,
                "email": user_data["email"],
                "full_name": user_data["full_name"],
                "role": user_data["role"],
                "is_active": user_data["is_active"],
                "created_at": user_data["created_at"]
            }
    return None

def authenticate_user(email: str, password: str):
    """Аутентификация пользователя"""
    for user_id, user_data in users_db.items():
        if user_data["email"] == email:
            if verify_password(password, user_data["password_hash"]):
                return {
                    "id": user_id,
                    "email": user_data["email"],
                    "full_name": user_data["full_name"],
                    "role": user_data["role"],
                    "is_active": user_data["is_active"],
                    "created_at": user_data["created_at"]
                }
    return None

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Регистрация пользователя"""
    # Проверяем, что пользователь не существует
    if get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Проверяем роль
    if user_data.role not in settings.USER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {settings.USER_ROLES}"
        )
    
    # Создаем пользователя
    user_id = f"user_{len(users_db) + 1}"
    password_hash = get_password_hash(user_data.password)
    
    user = {
        "email": user_data.email,
        "password_hash": password_hash,
        "full_name": user_data.full_name,
        "role": user_data.role,
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    users_db[user_id] = user
    
    return UserResponse(
        id=user_id,
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"],
        is_active=user["is_active"],
        created_at=user["created_at"]
    )

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Вход в систему"""
    user = authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token, expires_at = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at,
        user=UserResponse(**user)
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: dict = Depends(verify_token)):
    """Получить информацию о текущем пользователе"""
    return UserResponse(**current_user)

@router.post("/logout")
async def logout(current_user: dict = Depends(verify_token)):
    """Выход из системы"""
    # В реальной системе здесь можно добавить токен в blacklist
    return {"message": "Successfully logged out"}

@router.post("/refresh")
async def refresh_token(current_user: dict = Depends(verify_token)):
    """Обновление токена"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token, expires_at = create_access_token(
        data={"sub": current_user["email"]}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": expires_at
    }

# Инициализация тестовых пользователей
def init_test_users():
    """Создание тестовых пользователей"""
    test_users = [
        {
            "id": "admin_1",
            "email": "admin@example.com",
            "password": "password",
            "full_name": "Администратор Системы",
            "role": "administrator"
        },
        {
            "id": "warehouse_1",
            "email": "warehouse@example.com",
            "password": "password",
            "full_name": "Кладовщик",
            "role": "warehouse_keeper"
        },
        {
            "id": "qc_1",
            "email": "qc@example.com",
            "password": "password",
            "full_name": "Контролер ОТК",
            "role": "quality_control"
        },
        {
            "id": "lab_destructive_1",
            "email": "lab_destructive@example.com",
            "password": "password",
            "full_name": "Лаборант разрушающих испытаний",
            "role": "lab_destructive"
        },
        {
            "id": "lab_non_destructive_1",
            "email": "lab_non_destructive@example.com",
            "password": "password",
            "full_name": "Лаборант неразрушающих испытаний",
            "role": "lab_non_destructive"
        },
        {
            "id": "production_1",
            "email": "production@example.com",
            "password": "password",
            "full_name": "Специалист производства",
            "role": "production"
        }
    ]
    
    for user_data in test_users:
        user_id = user_data["id"]
        password_hash = get_password_hash(user_data["password"])
        
        user = {
            "email": user_data["email"],
            "password_hash": password_hash,
            "full_name": user_data["full_name"],
            "role": user_data["role"],
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        users_db[user_id] = user

# Инициализируем тестовых пользователей при загрузке модуля
init_test_users()