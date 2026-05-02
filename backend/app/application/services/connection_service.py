from typing import List

from app.application.schemas import ConnectionCreate, ConnectionResponse
from app.core.exceptions import ResourceNotFoundError
from app.domain.entities.connection import ConnectionConfig
from app.domain.interfaces.repository import ConnectionRepository
from app.infrastructure.repositories.memory_repository import connection_repository


class ConnectionService:
    def __init__(self, repository: ConnectionRepository):
        self._repository = repository

    async def create_connection(self, data: ConnectionCreate, owner_id: str) -> ConnectionResponse:
        connection = ConnectionConfig(**data.model_dump(), owner_id=owner_id)
        created = await self._repository.create(connection)
        return ConnectionResponse.model_validate(created.model_dump())

    async def get_all_connections(self, owner_id: str) -> List[ConnectionResponse]:
        connections = await self._repository.get_all()
        owned_connections = [c for c in connections if getattr(c, "owner_id", None) == owner_id]
        return [ConnectionResponse.model_validate(c.model_dump()) for c in owned_connections]

    async def get_connection(self, id: str, owner_id: str) -> ConnectionResponse:
        connection = await self._repository.get_by_id(id)
        if not connection or getattr(connection, "owner_id", None) != owner_id:
            raise ResourceNotFoundError("Connection", id)
        return ConnectionResponse.model_validate(connection.model_dump())

    async def delete_connection(self, id: str, owner_id: str) -> bool:
        connection = await self._repository.get_by_id(id)
        if not connection or getattr(connection, "owner_id", None) != owner_id:
            raise ResourceNotFoundError("Connection", id)
        success = await self._repository.delete(id)
        if not success:
            raise ResourceNotFoundError("Connection", id)
        return True


connection_service = ConnectionService(connection_repository)
