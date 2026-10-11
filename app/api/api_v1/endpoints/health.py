from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    """
    Liveness check for the hosting platform. Does not touch the database.
    """
    return {"status": "ok"}
