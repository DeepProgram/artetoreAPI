from pydantic import BaseModel


class GroupImageList(BaseModel):
    all_group_image: dict
    selected_group: dict


class OnedriveAuth(BaseModel):
    auth_code: str


class AddImageList(BaseModel):
    image_list: dict
