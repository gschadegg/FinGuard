from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services.user_service import UserService
from app.services_container import get_user_service
from app.domain.entities import UserEntity
from app.domain.errors import NotFoundError, ConflictError

router = APIRouter(prefix="/users", tags=["users"])

# this is an example to figure out the structure and workflow I want to follow
@router.post("", response_model=UserEntity, status_code=status.HTTP_201_CREATED)
async def create_user(email: str, name: str, svc: UserService = Depends(get_user_service)):
    try:
        return await svc.create_user(email=email, name=name)
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.get("", response_model=List[UserEntity])
async def list_users(svc: UserService = Depends(get_user_service)):
    return await svc.list_users()

@router.get("/{user_id}", response_model=UserEntity)
async def get_user(user_id: int, svc: UserService = Depends(get_user_service)):
    try:
        return await svc.get_user(user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, svc: UserService = Depends(get_user_service)):
    try:
        await svc.delete_user(user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))