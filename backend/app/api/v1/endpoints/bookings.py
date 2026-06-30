from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_bookings():
    return {"message": "Bookings endpoints stub active"}
