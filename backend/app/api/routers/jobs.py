import asyncio
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from typing import List
from app.api.deps import get_current_active_user, get_job_orchestrator
from app.application.schemas import JobCreate, JobResponse
from app.application.services.job_orchestrator import JobOrchestrator
from app.core.exceptions import ResourceNotFoundError
from app.domain.entities.user import User

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    data: JobCreate,
    orchestrator: JobOrchestrator = Depends(get_job_orchestrator),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return await orchestrator.create_job(data, current_user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    orchestrator: JobOrchestrator = Depends(get_job_orchestrator),
    current_user: User = Depends(get_current_active_user),
):
    return await orchestrator.get_all_jobs(current_user.id)

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    orchestrator: JobOrchestrator = Depends(get_job_orchestrator),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return await orchestrator.get_job(job_id, current_user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{job_id}/run", status_code=status.HTTP_202_ACCEPTED)
async def run_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    orchestrator: JobOrchestrator = Depends(get_job_orchestrator),
    current_user: User = Depends(get_current_active_user),
):
    try:
        await orchestrator.get_job(job_id, current_user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    background_tasks.add_task(orchestrator.run_job, job_id, current_user.id)
    return {"message": "Job execution started in the background."}
