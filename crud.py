from typing import Union

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from db.db_models import ImageDB, OnedriveDB, UserDB


def get_last_group(db: Session):
    try:
        group_list = db.query(ImageDB.image_group).group_by(ImageDB.image_group).all()
        last_group = group_list[-1][0]
    except Exception:
        last_group = 0
    return last_group


def get_group_list(db: Session):
    try:
        group_list = db.query(ImageDB.image_group, ImageDB.image_id, ImageDB.image_name).group_by(
            ImageDB.image_group).all()
        group_list = list(map(lambda x: x[0], group_list))
    except Exception as e:
        print(e)
        group_list = []
    return group_list


def get_group_last_image_id(db: Session, group):
    last_image_id, = db.query(ImageDB.image_id).order_by(ImageDB.index.desc()).filter(
        ImageDB.image_group == group).first()
    return last_image_id


def get_group_list_with_images_from_db(db: Session):
    group_list = db.query(ImageDB.image_group, ImageDB.image_folder, ImageDB.image_id, ImageDB.image_name).all()
    return group_list


def add_image_info_in_database(db: Session, image_list, selected_group, folder_name):
    if selected_group == -1:
        selected_group = get_last_group(db) + 1
        last_image_id = 1
    else:
        last_image_id = get_group_last_image_id(db, selected_group) + 1
    for image_info in image_list:
        image_db_data = ImageDB(selected_group, folder_name,
                                last_image_id,
                                image_info["file_name"], image_info["title"],
                                image_info["low_res_image"], image_info["high_res_image"], image_info["full_image"])
        db.add(image_db_data)
        db.commit()
        last_image_id += 1
    return None


def delete_image_from_database(db: Session, group_id, image_id):
    db.query(ImageDB).filter(ImageDB.image_group == group_id, ImageDB.image_id == image_id).delete()
    db.commit()


def get_image_per_page(db: Session, page: int):
    status = 1
    last_group = get_last_group(db)
    start_group, end_group = 0, 0

    if ((page - 1) * 12) + 1 <= last_group:
        start_group = ((page - 1) * 12) + 1
        if page * 12 >= last_group:
            end_group = last_group
        else:
            end_group = page * 12
    else:
        status = 0

    image_list = []
    if status == 1:
        for group_id in range(start_group, end_group + 1):
            group_first_image_data = db.query(ImageDB.image_group, ImageDB.image_name, ImageDB.low_res_image).filter(
                ImageDB.image_group == group_id).first()
            image_list.append({
                "group": group_first_image_data[0],
                "image_name": group_first_image_data[1],
                "image": group_first_image_data[2]
            })
    return status, image_list


def get_image_from_group(db: Session, group):
    image_info_list = db.query(ImageDB.image_group, ImageDB.image_id, ImageDB.image_name, ImageDB.low_res_image).filter(
        ImageDB.image_group == group).all()
    image_list = []
    for image_data in image_info_list:
        image_list.append(
            {
                "group": image_data[0],
                "imageID": image_data[1],
                "imageName": image_data[2],
                "image": image_data[3]
            }
        )
    return image_list


def get_one_image(db: Session, group: int, image_id: int):
    image_info = db.query(ImageDB.image_name, ImageDB.high_res_image).filter(ImageDB.image_group == group,
                                                                             ImageDB.image_id == image_id).first()
    if image_info is None:
        return None
    image_info_dict = {
        "imageName": image_info[0],
        "image": image_info[1]
    }
    return image_info_dict


def download_full_image(db: Session, group_id: int, image_id: int):
    full_image = db.query(ImageDB.image_name, ImageDB.full_image).filter(ImageDB.image_group == group_id,
                                                     ImageDB.image_id == image_id).first()
    if full_image is not None:
        return {
            "image_name": full_image[0],
            "image": full_image[1]
        }
    return None


def count_total_groups(db: Session):
    last_group, = db.query(ImageDB.image_group).order_by(ImageDB.image_group.desc()).first()
    return last_group


def get_hashed_password_from_username(db: Session, username: str):
    try:
        data = db.query(UserDB.password, UserDB.userid).filter(username == UserDB.username).first()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="database_not_found",
        )
    if data is not None:
        return data[0], data[1]
    return data, None


def add_tokens_in_database(db: Session, current_token, refresh_token, user_id):
    token_added = True
    try:
        db.query(OnedriveDB).filter(OnedriveDB.user_id == user_id).update({
            "current_token": current_token, "refresh_token": refresh_token})
        db.commit()
    except Exception:
        token_added = False

    return token_added


def get_tokens_from_user_id(user_id: str, db: Session):
    try:
        tokens = db.query(OnedriveDB.current_token, OnedriveDB.refresh_token).filter(
            OnedriveDB.user_id == user_id).first()
    except Exception:
        tokens = None
    if tokens is None:
        return None, None
    return tokens[0], tokens[1]


def get_low_res_image_from_db(db: Session, group_id: int, image_id: Union[int, None]):
    try:
        if image_id is None:
            image = db.query(ImageDB.low_res_image).filter(ImageDB.image_group == group_id).first()
        else:
            image = db.query(ImageDB.low_res_image).filter(ImageDB.image_group == group_id,
                                                           ImageDB.image_id == image_id).first()
        image = image[0]
    except Exception:
        image = None
    return image
