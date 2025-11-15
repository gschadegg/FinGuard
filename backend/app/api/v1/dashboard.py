from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from app.domain.entities import DashboardEntity

from app.security.auth import get_current_user
from app.services_container import get_dashboard_service

from app.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=DashboardEntity)
async def get_dashboard(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    svc: DashboardService = Depends(get_dashboard_service),
    current_user = Depends(get_current_user),
):
    try:
        return await svc.get_dashboard(
            user_id=current_user.id,
            year=year,
            month=month,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    