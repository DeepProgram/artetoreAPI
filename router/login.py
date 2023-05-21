from fastapi import APIRouter, Depends, status
from starlette.responses import JSONResponse
from router.image import get_db
from sqlalchemy.orm import Session
from logic.admin import verify_login

router = APIRouter(
    prefix="/login",
    tags=["login"]
)


@router.get("/")
async def login(username: str, password: str, db: Session = Depends(get_db)):
    result, new_token = verify_login(db, username, password)
    if result == 2:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 2,
                "token": new_token
            }
        )
    elif result == 0:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "hint": "username or password did not match"
            }
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 1,
            "hint": "username or password did not match"
        }
    )



