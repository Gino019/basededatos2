import json
import uuid
from typing import List, Optional

import motor.motor_asyncio

from app.domain.entities.connection import ConnectionConfig
from app.domain.interfaces.repository import ConnectionRepository


class MongoDBConnectionRepository(ConnectionRepository):
    def __init__(self, uri: str, metadata_database: str = "enmask_meta"):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client[metadata_database]
        self.collection = self.db["connections"]

    async def create(self, entity: ConnectionConfig) -> ConnectionConfig:
        entity_dict = entity.model_dump()
        entity_dict["id"] = entity_dict.get("id") or str(uuid.uuid4())
        entity_dict["additional_options"] = json.dumps(entity_dict.get("additional_options", {}))
        await self.collection.insert_one(entity_dict)
        return ConnectionConfig(**entity_dict)

    async def get_by_id(self, id: str) -> Optional[ConnectionConfig]:
        data = await self.collection.find_one({"id": id})
        if not data:
            return None
        data["additional_options"] = json.loads(data.get("additional_options", "{}"))
        return ConnectionConfig(**data)

    async def get_all(self) -> List[ConnectionConfig]:
        cursor = self.collection.find({})
        records = []
        async for doc in cursor:
            doc["additional_options"] = json.loads(doc.get("additional_options", "{}"))
            records.append(ConnectionConfig(**doc))
        return records

    async def update(self, id: str, entity: ConnectionConfig) -> Optional[ConnectionConfig]:
        entity_dict = entity.model_dump()
        entity_dict["additional_options"] = json.dumps(entity_dict.get("additional_options", {}))
        result = await self.collection.update_one({"id": id}, {"$set": entity_dict})
        if result.modified_count:
            return ConnectionConfig(**entity_dict)
        return None

    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"id": id})
        return result.deleted_count == 1
