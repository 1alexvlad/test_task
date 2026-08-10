from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.exc import IntegrityError

from models.users import User
from schemas.users import SAdminUsersShow, SUserCreate, SAboutMe, SUserUpdate
from services.users import UsersServices
from core.dependencies import get_current_admin

from core.auth import get_password_hash


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get('/users')
async def all_users(user_data: User = Depends(get_current_admin)) -> list[SAdminUsersShow]:
    users = await UsersServices.find_all()
    return users

@router.get('/me')
async def get_me(current_user: User = Depends(get_current_admin)) -> SAboutMe:
    return SAboutMe(id=current_user.id, email=current_user.email, full_name=current_user.full_name)


@router.post('/create_user')
async def create_user(data: SUserCreate, user_data: User = Depends(get_current_admin)) -> SAboutMe:

    hashed_password = get_password_hash(data.password)
    try:
        user = await UsersServices.create_user(
            email=data.email,
            password=hashed_password,
            full_name=data.full_name,
            is_admin=data.is_admin
        )
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким email уже существует")

    return user


@router.delete('/delete_user/{user_id}')
async def delete_user(user_id: int, user_data: User = Depends(get_current_admin)) -> dict:

    try:
        await UsersServices.delete_user(user_id)
        return {"message": f"Пользователь с id={user_id} успешно удалён"}
    except ValueError:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при удалении пользователя")

@router.patch('/update_user/{user_id}')
async def updaste_user(user_id: int, data: SUserUpdate, user_data: User = Depends(get_current_admin)) -> SAboutMe:
    user = await UsersServices.find_one_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    update_data = data.model_dump(exclude_unset=True)

    if 'password' in update_data:
        update_data["password"] = get_password_hash(update_data["password"])

    updated_user = await UsersServices.update(user_id, **update_data)
    return updated_user
