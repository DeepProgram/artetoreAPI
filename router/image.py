from fastapi import APIRouter, Depends, status
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session

from db.sql_db import SessionLocal
from crud import get_image_per_page, get_image_from_group, get_one_image, get_last_group, download_full_image

router = APIRouter(
    prefix="/image",
    tags=["image"]
)


def get_db():
    db = None
    try:
        db = SessionLocal()
        return db
    finally:
        db.close()


@router.get("/")
async def get_single_image(group: int, image_id: int, db: Session = Depends(get_db)):
    image_info = get_one_image(db, group, image_id)
    if image_info is None:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "hint": "image_not_found"
            }
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 1,
            "data": image_info,
            "hint": 'image_found'
        }
    )


@router.get("/page")
async def get_image(page: int = 1, db: Session = Depends(get_db)):
    if page < 1:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": -1,
                "hint": "positive invalid page.. dont try this again"
            }
        )
    code, image_list = get_image_per_page(db, page)
    if code == 0:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "hint": "database_empty"
            }
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 1,
            "data": image_list,
            "hint": "got_images"
        }
    )


@router.get("/group")
async def get_group_image(group: int = 1, db: Session = Depends(get_db)):
    image_list = get_image_from_group(db, group)
    if not image_list:
        return {
            "status": 0,
            "data": "invalid group.. dont try this again"
        }
    return {
        "status": 1,
        "data": image_list
    }


@router.get("/total-page")
async def get_total_pages(db: Session = Depends(get_db)):
    total = get_last_group(db)
    pages = total // 12
    if total % 12 != 0:
        pages += 1
    return {
        "totalPage": pages
    }


@router.get("/download")
async def download_operation(group_id: int, image_id: int, db: Session = Depends(get_db)):
    image = download_full_image(db, group_id, image_id)
    if image is not None:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 1,
                "image": image,
                "hint": "image_found"
            }
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 0,
            "hint": "image_not_found"
        }
    )
