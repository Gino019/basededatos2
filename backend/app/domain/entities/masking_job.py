from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class MaskingJob(BaseModel):
    id: Optional[str] = None
    connection_id: str
    rule_ids: List[str]
    status: JobStatus = JobStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    records_processed: int = 0
    owner_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
