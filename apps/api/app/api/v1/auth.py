from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentAuth, DbSession
from app.core.plans import get_limits
from app.schemas import LoginRequest, OrganizationOut, SignupRequest, TokenResponse, UserOut, WorkspaceOut
from app.services import auth_service

router = APIRouter()


@router.post("/signup", response_model=TokenResponse)
async def signup(body: SignupRequest, db: DbSession):
    try:
        user, org, ws, token = await auth_service.signup(
            db,
            email=body.email,
            password=body.password,
            full_name=body.full_name,
            organization_name=body.organization_name,
            workspace_name=body.workspace_name,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return TokenResponse(access_token=token, org_id=org.id, workspace_id=ws.id)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: DbSession):
    try:
        user, org, ws, token = await auth_service.login(db, email=body.email, password=body.password)
    except ValueError as exc:
        raise HTTPException(401, str(exc)) from exc
    return TokenResponse(
        access_token=token,
        org_id=org.id,
        workspace_id=ws.id if ws else None,
    )


@router.get("/me")
async def me(auth: CurrentAuth):
    return {
        "user": UserOut.model_validate(auth.user),
        "organization": OrganizationOut.model_validate(auth.organization),
        "role": auth.membership.role.value,
        "subscription": {
            "tier": auth.subscription.tier.value,
            "status": auth.subscription.status,
            "credits_balance": auth.subscription.credits_balance,
            "auto_apply_enabled": auth.subscription.auto_apply_enabled,
            "limits": get_limits(auth.tier),
        },
    }
