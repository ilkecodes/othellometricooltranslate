from fastapi import APIRouter

router = APIRouter()

@router.get('/')
async def list_curriculum():
    return {"curriculum": []}

@router.post('/')
async def create_curriculum(item: dict):
    return {"id": 1, **item}
