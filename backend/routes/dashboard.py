from fastapi import APIRouter

from database.queries import get_latest_attributes

router = APIRouter()


@router.get("/policies")
def list_policies():
    return get_latest_attributes()
