import base64
import io
import json
from typing import Union

import requests
from PIL import Image, ImageOps
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from crud import get_hashed_password_from_username, add_tokens_in_database, get_tokens_from_user_id, \
    add_image_info_in_database, get_low_res_image_from_db, get_group_list_with_images_from_db, \
    delete_image_from_database
from logic.cryptography import verify_password
from logic.token import create_jwt_access_token
import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
folder_arts_id = os.getenv("folder_arts_id")

permissions = ['offline_access', 'files.readwrite', 'User.Read']
response_type = 'code'
redirect_uri = 'http://localhost:3000/connect/onedrive/auth'
scope = ''
for items in range(len(permissions)):
    scope = scope + permissions[items]
    if items < len(permissions) - 1:
        scope = scope + '+'

local_tokens = {
    "current_token": None,
    "refresh_token": None
}


def generate_onedrive_auth_url():
    return f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={client_id}&scope={scope}&response_type=code&redirect_uri={redirect_uri}"


def process_token_from_response_data_and_add_in_db(response_data: str, db: Session, user_id: str):
    found_tokens = True
    current_token, refresh_token = None, None
    try:
        current_token = json.loads(response_data)["access_token"]
        refresh_token = json.loads(response_data)["refresh_token"]
    except Exception:
        found_tokens = False

    if found_tokens:
        add_tokens_in_database(db, current_token, refresh_token, user_id)
        local_tokens["current_token"] = current_token
        local_tokens["refresh_token"] = refresh_token
    return found_tokens


def get_tokens_from_auth_code(db: Session, auth_code: str, user_id: str):
    token_request_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    response = requests.post(token_request_url, data={
        "client_id": client_id,
        "code": auth_code,
        "redirect_uri": redirect_uri,
        "client_secret": client_secret,
        "grant_type": "authorization_code"
    })
    return process_token_from_response_data_and_add_in_db(response.text, db, user_id)


def verify_login(db: Session, username: str, password: str):
    hashed_password, user_id = get_hashed_password_from_username(db, username)
    if hashed_password is None:
        return 0, None
    if verify_password(password, hashed_password):
        new_token = create_jwt_access_token(user_id, None)
        return 2, new_token
    return 1, None


def get_new_token_from_refresh_token(refresh_token, db: Session, user_id: str):
    token_request_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
    response = requests.post(token_request_url, data={
        "client_id": client_id,
        "refresh_token": refresh_token,
        "redirect_uri": redirect_uri,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    })
    return process_token_from_response_data_and_add_in_db(response.text, db, user_id)


def get_token_from_db(db: Session, user_id: str):
    if local_tokens["current_token"] is None:
        current_token, refresh_token = get_tokens_from_user_id(user_id, db)
        if current_token is not None:
            local_tokens["current_token"] = current_token
            local_tokens["refresh_token"] = refresh_token
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="database_not_found",
            )


def connect_onedrive(db: Session, user_id: str):
    get_token_from_db(db, user_id)

    response = requests.get("https://graph.microsoft.com/v1.0/",
                            headers={'Authorization': 'Bearer ' + local_tokens["current_token"]})
    response_status_code = response.status_code
    connection_onedrive_dict = {
        "connected": 0  # Connection Failed
    }

    if response_status_code == 200:
        connection_onedrive_dict["connected"] = 1  # Connection Successful
    elif response_status_code == 401:
        found_tokens = get_new_token_from_refresh_token(local_tokens["refresh_token"], db, user_id)
        if found_tokens:
            connection_onedrive_dict["connected"] = 1  # Refreshed Token Connection Successful

    return connection_onedrive_dict


def get_files_from_folder(item_id, db, user_id):
    response = requests.get(f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}/children",
                            headers={'Authorization': 'Bearer ' + local_tokens["current_token"]})
    files_dict = {}
    if response.status_code == 200:
        try:
            response_data = json.loads(response.text)
            for file in response_data["value"]:
                if file.get("folder") is not None:
                    continue
                files_dict[file["id"]] = {
                    "file_name": file["name"],
                    "file_size": file["size"],
                    "creation_time": file["fileSystemInfo"]["createdDateTime"],
                    "modification_time": file["fileSystemInfo"]["lastModifiedDateTime"],
                    "is_folder": False
                }
            return 1, files_dict  # 1 Is For Success
        except Exception:
            print("Exception Found 2")
            return 2, {}
    elif response.status_code == 401:
        found_tokens = get_new_token_from_refresh_token(local_tokens["refresh_token"], db, user_id)
        if found_tokens:
            return get_files_from_folder(item_id, db, user_id)
    return 0, files_dict  # 0 Is For Failure.  Need New Current Token By Manual Authorization


def get_folders(db: Session, user_id):
    get_token_from_db(db, user_id)
    folders_info_dict = {}
    try:
        response = json.loads(requests.get('https://graph.microsoft.com/v1.0/me/drive/', headers={'Authorization': 'Bearer ' + local_tokens["current_token"]}).text)
        used = round(response['quota']['used'] / (1024 * 1024 * 1024), 2)
        total = round(response['quota']['total'] / (1024 * 1024 * 1024), 2)
        folders_info_dict["used_storage"] = used
        folders_info_dict["total_storage"] = total
    except Exception:
        return 0, {}
    try:
        response = requests.get(
            f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_arts_id}/children",
            headers={'Authorization': 'Bearer ' + local_tokens["current_token"]})
    except Exception:
        print("Couldn't Connect To Microsoft APi")
        return 0, {}

    if response.status_code == 200:
        print("Response From Folder 1 200")
        try:
            response_data = json.loads(response.text)

            for item in response_data["value"]:
                if item.get("file") is not None:
                    continue
                valid_current_token, files_dict = get_files_from_folder(item["id"], db, user_id)
                folders_info_dict[item["id"]] = {
                    "folder_name": item["name"],
                    "folder_size": item["size"],
                    "creation_time": item["fileSystemInfo"]["createdDateTime"],
                    "modification_time": item["fileSystemInfo"]["lastModifiedDateTime"],
                    "is_folder": True,
                    "files": files_dict.copy()
                }
                if valid_current_token == 0:
                    return 0, {}
                if valid_current_token == 2:
                    return 2, {}
            return 1, folders_info_dict
        except Exception:
            print("Exception Found 1")
            return 2, {}
    elif response.status_code == 401:
        print("Response From Folder 2 Unknown")
        found_tokens = get_new_token_from_refresh_token(local_tokens["refresh_token"], db, user_id)
        if found_tokens:
            return get_folders(db, user_id)
    print("Response From Folder 3 Unknown")
    return 0, folders_info_dict  # 0 Is For Failure.  Need New Current Token By Manual Authorization


def rename_onedrive_item(db: Session, user_id: str, item_id, new_name):
    get_token_from_db(db, user_id)
    response = requests.patch(f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}",
                              headers={'Authorization': 'Bearer ' + local_tokens["current_token"]},
                              json={"name": new_name})
    if response.status_code == 200:
        return 1
    elif response.status_code == 401:
        found_tokens = get_new_token_from_refresh_token(local_tokens["refresh_token"], db, user_id)
        if found_tokens:
            return rename_onedrive_item(db, user_id, item_id, new_name)
    return 0


def create_folder_in_onedrive(db: Session, user_id, folder_name: str):
    get_token_from_db(db, user_id)
    body = {
        "name": folder_name,
        "folder": {},
        "@microsoft.graph.conflictBehavior": "rename"
    }
    response = requests.post(f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_arts_id}"
                             "/children", headers={'Authorization': 'Bearer ' + local_tokens["current_token"]},
                             json=body)

    if response.status_code == 201:
        return 1
    elif response.status_code == 401:
        found_tokens = get_new_token_from_refresh_token(local_tokens["refresh_token"], db, user_id)
        if found_tokens:
            return create_folder_in_onedrive(db, user_id, folder_name)
    return 0


def delete_folder_from_onedrive(db: Session, user_id: str, folder_id):
    get_token_from_db(db, user_id)
    response = requests.delete(f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}",
                               headers={'Authorization': 'Bearer ' + local_tokens["current_token"]})
    if response.status_code == 204:
        return 1
    elif response.status_code == 401:
        found_tokens = get_new_token_from_refresh_token(local_tokens["refresh_token"], db, user_id)
        if found_tokens:
            return delete_folder_from_onedrive(db, user_id, folder_id)
    return 0


def get_onedrive_uploading_session(db: Session, user_id: str, folder_id, file_name):
    get_token_from_db(db, user_id)
    response = requests.post(f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}"
                             f":/{file_name}:/createUploadSession",
                             headers={'Authorization': 'Bearer ' + local_tokens["current_token"]})

    if response.status_code == 200:
        upload_url = json.loads(response.text)["uploadUrl"]

        return 1, upload_url
    if response.status_code == 401:
        found_tokens = get_new_token_from_refresh_token(local_tokens["refresh_token"], db, user_id)
        if found_tokens:
            return get_onedrive_uploading_session(db, user_id, folder_id, file_name)
    return 0, None


def download_image_content(db, user_id, file_id):
    get_token_from_db(db, user_id)
    response = requests.get(f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content",
                            headers={'Authorization': 'Bearer ' + local_tokens["current_token"]})

    if response.status_code == 200:
        return response.content
    return None


def add_image_in_database(db: Session, user_id: str, image_list: dict):
    for folder_key, folder_value in image_list.items():
        all_images = []
        for image_info in folder_value["all_image_id"]:
            image_data = download_image_content(db, user_id, image_info["file_id"])
            if image_data is not None:
                image_dict = generate_image_dict_for_database(image_data, image_info["file_name"])
                if image_data is not None:
                    all_images.append(image_dict.copy())
        add_image_info_in_database(db, all_images, folder_value["group"], folder_value["folder_name"], )
    return 1


def generate_image_dict_for_database(img_as_byte, file_name):
    low_res_image = change_image_resolution(img_as_byte, 180, 115)
    if low_res_image is None:
        return None
    high_res_image = change_image_resolution(img_as_byte, 700, 525)
    high_res_image_base64 = convert_image_into_base64(high_res_image)
    low_res_image_base64 = convert_image_into_base64(low_res_image)
    full_image = convert_image_into_base64(img_as_byte)
    title = "This Is Sample Title"
    return {
        "title": title,
        "file_name": file_name,
        "low_res_image": low_res_image_base64,
        "high_res_image": high_res_image_base64,
        "full_image": full_image
    }


def change_image_resolution(image_data, target_width, target_height):
    try:
        im = Image.open(io.BytesIO(image_data))
    except Exception:
        return None
    fixed_image = ImageOps.exif_transpose(im)
    im_resize = fixed_image.resize((target_width, target_height))
    buf = io.BytesIO()
    im_resize.save(buf, format=im.format)
    byte_im = buf.getvalue()
    return byte_im


def convert_image_into_base64(image_as_byte):
    encoded = base64.b64encode(image_as_byte).decode('ascii')
    base64_image_data = 'data:image/{};base64,{}'.format("png", encoded)
    return base64_image_data


def get_one_low_res_image_from_group(db: Session, group_id: int, image_id: Union[int, None]):
    image = get_low_res_image_from_db(db, group_id, image_id)
    if image is None:
        return 0, image
    return 1, image


def get_group_list_with_images(db: Session):
    group_list = get_group_list_with_images_from_db(db)
    group_dict = {}
    for data in group_list:
        if group_dict.get(data[0]) is None:
            group_dict[data[0]] = {
                "images": [{
                    "folder_name": data[1],
                    "image_id": data[2],
                    "image_name": data[3]
                }]
            }
        else:
            group_dict[data[0]]["images"].append({
                "folder_name": data[1],
                "image_id": data[2],
                "image_name": data[3]
            })
    return group_dict


def delete_image(db: Session, image_list: dict):
    for key, value in image_list.items():
        for image in value:
            delete_image_from_database(db, key, image["image_id"])
    return 1
