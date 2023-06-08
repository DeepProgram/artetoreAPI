from typing import Union
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from crud import get_group_list
from logic.admin import generate_onedrive_auth_url, get_tokens_from_auth_code, connect_onedrive, get_folders, \
    rename_onedrive_item, create_folder_in_onedrive, delete_folder_from_onedrive, \
    get_onedrive_uploading_session, add_image_in_database, get_one_low_res_image_from_group, get_group_list_with_images, \
    delete_image
from logic.token import get_current_user_from_jwt_token, oauth2_bearer
from schema import OnedriveAuth, AddImageList
from router.image import get_db

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


@router.post("/auth/code")
async def get_onedrive_auth_code(auth_info: OnedriveAuth, token: str = Depends(oauth2_bearer),
                                 db: Session = Depends(get_db)):
    user_id = get_current_user_from_jwt_token(token)
    auth_code = auth_info.auth_code
    result = get_tokens_from_auth_code(db, auth_code, user_id)
    if result:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 1,
                "hint": "found_tokens"
            }
        )
    url = generate_onedrive_auth_url()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 0,
            "hint": "found_tokens_failed",
            "url": url
        }
    )


@router.get("/onedrive/connect")
async def onedrive_connection(token: str = Depends(oauth2_bearer), db: Session = Depends(get_db)):
    user_id = get_current_user_from_jwt_token(token)
    connection_dict = connect_onedrive(db, user_id)
    if connection_dict["connected"] == 1:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 1,
                "hint": "connection_successful"
            }
        )
    url = generate_onedrive_auth_url()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 0,
            "hint": "connection_failed",
            "url": url
        }
    )


@router.get("/onedrive/folders")
async def onedrive_folders(token: str = Depends(oauth2_bearer), db: Session = Depends(get_db)):
    user_id = get_current_user_from_jwt_token(token)
    token_status, folders = get_folders(db, user_id)
    if token_status == 0:
        url = generate_onedrive_auth_url()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "hint": "refresh_token_expired_need_manual_authorization",
                "url": url
            }
        )
    if token_status == 2:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 99,
                "hint": "data_extraction_failed_from_json"
            }
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 1,
            "folders": folders
        }
    )


@router.get("/onedrive/rename")
async def rename_operation(item_id: str, new_name: str, token: str = Depends(oauth2_bearer),
                           db: Session = Depends(get_db)):
    user_id = get_current_user_from_jwt_token(token)
    result = rename_onedrive_item(db, user_id, item_id, new_name)

    if result == 1:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 1,
                "hint": "rename_operation_successful"
            }
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 0,
            "hint": "rename_operation_failed"
        }
    )


@router.get("/onedrive/add-folder")
async def add_folder_operation(folder_name: str, token: str = Depends(oauth2_bearer), db: Session = Depends(get_db)):
    user_id = get_current_user_from_jwt_token(token)
    result = create_folder_in_onedrive(db, user_id, folder_name)
    if result == 1:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 1,
                "hint": "folder_creation_operation_successful"
            }
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 0,
            "hint": "folder_creation_operation_failed"
        }
    )


@router.get("/onedrive/delete-folder")
async def folder_delete_operation(folder_id: str, token: str = Depends(oauth2_bearer), db: Session = Depends(get_db)):
    user_id = get_current_user_from_jwt_token(token)
    result = delete_folder_from_onedrive(db, user_id, folder_id)
    if result == 1:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 1,
                "hint": "folder_deletion_operation_successful"
            }
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 0,
            "hint": "folder_deletion_operation_failed"
        }
    )


@router.get("/onedrive/upload-session")
async def file_upload_session(folder_id: str, file_name: str, token: str = Depends(oauth2_bearer),
                              db: Session = Depends(get_db)):
    user_id = get_current_user_from_jwt_token(token)
    success_status, upload_url = get_onedrive_uploading_session(db, user_id, folder_id, file_name)
    if success_status == 1:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 1,
                "sessionUrl": upload_url,
                "hint": "got_session"
            }
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 0,
            "hint": "couldn't_get_session"
        }
    )


@router.get("/groups")
async def group_list(token: str = Depends(oauth2_bearer), db: Session = Depends(get_db)):
    user_id = get_current_user_from_jwt_token(token)
    groups = get_group_list(db)
    return {
        "data": groups
    }


@router.post("/add/image")
async def add_image_in_database_operation(image_list: AddImageList, token: str = Depends(oauth2_bearer),
                                          db: Session = Depends(get_db)):
    user_id = get_current_user_from_jwt_token(token)
    result = add_image_in_database(db, user_id, image_list.image_list)
    if result == 1:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 1,
                "hint": "image_added_in_database"
            }
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 2,
            "hint": "invalid image list"
        }
    )


@router.post("/delete/image")
async def add_image_in_database_operation(image_list: AddImageList, token: str = Depends(oauth2_bearer),
                                          db: Session = Depends(get_db)):
    user_id = get_current_user_from_jwt_token(token)
    result = delete_image(db, image_list.image_list)
    if result == 1:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 1,
                "hint": "image_deleted_from_database"
            }
        )


@router.get("/image")
async def get_single_image_from_group(group_id: int, image_id: Union[int, None] = None, token: str = Depends(oauth2_bearer),
                                      db: Session = Depends(get_db)):
    user_id = get_current_user_from_jwt_token(token)
    code, image = get_one_low_res_image_from_group(db, group_id, image_id)
    if code == 1:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 1,
                "image": image,
                "hint": "got_image"
            }
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 0,
            "hint": "couldn't_get_image"
        }
    )


@router.get("/groups/images")
async def get_groups_with_images(token: str = Depends(oauth2_bearer),
                                 db: Session = Depends(get_db)):
    user_id = get_current_user_from_jwt_token(token)
    result = get_group_list_with_images(db)
    if result == {}:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "hint": "empty_database"
            }
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 1,
            "data": result
        }
    )
