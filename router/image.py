from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.sql_db import SessionLocal
from crud import get_image_per_page, get_image_from_group, get_one_image, get_last_group

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
    return {
        "data": image_info
    }


@router.get("/page")
async def get_image(page: int = 1, db: Session = Depends(get_db)):
    if page < 1:
        return {
            "status": 0,
            "data": "positive invalid page.. dont try this again"
        }
    status, image_list = get_image_per_page(db, page)
    if status == 0:
        return {
            "status": 0,
            "data": "positive invalid page.. dont try this again"
        }
    return {
        "status": 1,
        "data": image_list
    }


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
