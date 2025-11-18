from fastapi import APIRouter

router = APIRouter()

@router.get('/')
async def list_teachers():
    return [{"id":1, "name":"Teacher A"}]
