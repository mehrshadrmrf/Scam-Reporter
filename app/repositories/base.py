from typing import Generic, Optional, Sequence, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self._session = session
        self._model = model

    async def get_by_id(self, entity_id: UUID) -> Optional[ModelType]:
        return await self._session.get(self._model, entity_id)

    async def list_all(self, limit: int = 50, offset: int = 0) -> Sequence[ModelType]:
        stmt = select(self._model).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    def add(self, entity: ModelType) -> ModelType:
        self._session.add(entity)
        return entity

    async def delete(self, entity: ModelType) -> None:
        await self._session.delete(entity)

    async def flush(self) -> None:
        await self._session.flush()

    async def commit(self) -> None:
        await self._session.commit()
