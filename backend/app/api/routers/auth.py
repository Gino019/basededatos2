from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_auth_service, get_current_active_user, require_role
from app.application.schemas import GoogleAuthRequest, AuthResponse, UserResponse
from app.application.services.auth_service import AuthService
from app.domain.entities.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/google", response_model=AuthResponse)
async def login_with_google(data: GoogleAuthRequest, auth_service: AuthService = Depends(get_auth_service)):
    try:
        return await auth_service.authenticate_google(data.id_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.get("/me", response_model=UserResponse)
async def get_current_user(user: User = Depends(get_current_active_user)):
    return UserResponse.model_validate(user.model_dump())

@router.get("/users", response_model=list[UserResponse], dependencies=[Depends(require_role("admin"))])
async def list_users(auth_service: AuthService = Depends(get_auth_service)):
    users = await auth_service._repository.get_all()
    return [UserResponse.model_validate(user.model_dump()) for user in users]
