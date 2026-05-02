from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.api.deps import get_current_active_user, get_connection_service
from app.application.schemas import ConnectionCreate, ConnectionResponse
from app.application.services.connection_service import ConnectionService
from app.core.exceptions import ResourceNotFoundError
from app.domain.entities.user import User

router = APIRouter(prefix="/connections", tags=["Connections"])

@router.post("/", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_connection(
    data: ConnectionCreate,
    service: ConnectionService = Depends(get_connection_service),
    current_user: User = Depends(get_current_active_user),
):
    return await service.create_connection(data, current_user.id)

@router.get("/", response_model=List[ConnectionResponse])
async def list_connections(
    service: ConnectionService = Depends(get_connection_service),
    current_user: User = Depends(get_current_active_user),
):
    return await service.get_all_connections(current_user.id)

@router.get("/{conn_id}", response_model=ConnectionResponse)
async def get_connection(
    conn_id: str,
    service: ConnectionService = Depends(get_connection_service),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return await service.get_connection(conn_id, current_user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{conn_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(
    conn_id: str,
    service: ConnectionService = Depends(get_connection_service),
    current_user: User = Depends(get_current_active_user),
):
    try:
        await service.delete_connection(conn_id, current_user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
