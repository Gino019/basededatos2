from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.domain.value_objects.database_type import DatabaseType
from app.domain.value_objects.masking_algorithm import MaskingAlgorithm
from app.domain.entities.masking_job import JobStatus
from datetime import datetime

class ConnectionCreate(BaseModel):
    name: str
    type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    password: str
    additional_options: Optional[Dict[str, Any]] = None

class ConnectionResponse(ConnectionCreate):
    id: str

class RuleCreate(BaseModel):
    name: str
    connection_id: str
    target_table: str
    target_column: str
    strategy: MaskingAlgorithm
    strategy_options: Optional[Dict[str, Any]] = None

class RuleResponse(RuleCreate):
    id: str

class JobCreate(BaseModel):
    connection_id: str
    rule_ids: List[str]

class JobResponse(BaseModel):
    id: str
    connection_id: str
    rule_ids: List[str]
    status: JobStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    records_processed: int

class GoogleAuthRequest(BaseModel):
    id_token: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    picture: Optional[str] = None

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
