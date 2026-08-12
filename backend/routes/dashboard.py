from fastapi import APIRouter, Request

from database.queries import get_latest_attributes

router = APIRouter()


@router.get("/policies")
def list_policies(request: Request):
    return get_latest_attributes(workspace_id=request.state.workspace_id)
