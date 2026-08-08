from models.users import User
from services.base import BaseService

from database import async_session_maker
from sqlalchemy import insert, delete, select, update


class UsersServices(BaseService):
    model = User

    @classmethod
    async def create_user(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data).returning(cls.model)
            result = await session.execute(query)
            new_instance = result.scalar_one()  
            await session.commit()
            return new_instance
        
    @classmethod
    async def delete_user(cls, user_id):
        async with async_session_maker() as session:

            query_delete = delete(cls.model).where(cls.model.id == user_id)

            result = await session.execute(query_delete)
            await session.commit()

            if result.rowcount == 0:
                raise ValueError("Пользователь не найден")

    @classmethod
    async def update(cls, user_id: int, **data):
        async with async_session_maker() as session:
            query = (
                update(cls.model)
                .where(cls.model.id == user_id)
                .values(**data)
                .returning(cls.model)
            )
            result = await session.execute(query)
            updated_instance = result.scalar_one()
            await session.commit()
            return updated_instance

