from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.domain.entities import UserEntity
from app.domain.errors import ConflictError, UnauthorizedError
from app.services.auth_service import AuthService
from app.services_container import get_auth_service


class Register(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=8, max_length=128)

class Login(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserEntity



router = APIRouter(prefix="/auth", tags=["auth"]) 

@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def register(payload: Register, svc: AuthService = Depends(get_auth_service)):
    try:
        user, token = await svc.register(
            email=payload.email, 
            name=payload.name, 
            password=payload.password
        )
        return TokenOut(access_token=token, user=user)
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.post("/login", response_model=TokenOut)
async def login(payload: Login, svc: AuthService = Depends(get_auth_service)):
    try:
        user, token = await svc.login(email=payload.email, password=payload.password)
        return TokenOut(access_token=token, user=user)
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e))