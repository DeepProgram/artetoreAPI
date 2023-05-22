from sqlalchemy import Column, String, Integer
from db.sql_db import Base


class ImageDB(Base):
    __tablename__ = "imagedb"
    index = Column(Integer, primary_key=True, autoincrement=True)
    image_group = Column(Integer)
    image_folder = Column(String)
    image_id = Column(Integer)
    image_name = Column(String)
    title = Column(String)
    low_res_image = Column(String)
    high_res_image = Column(String)
    full_image = Column(String)

    def __init__(self, image_group, image_folder, image_id, image_name, title, low_res_image, high_res_image, full_image):
        self.image_group = image_group
        self.image_folder = image_folder
        self.image_id = image_id
        self.image_name = image_name
        self.title = title
        self.full_image = full_image
        self.high_res_image = high_res_image
        self.low_res_image = low_res_image


class UserDB(Base):
    __tablename__ = "userdb"
    userid = Column(String, primary_key=True)
    username = Column(String)
    password = Column(String)

    def __init__(self, userid, username, password):
        self.userid = userid
        self.username = username
        self.password = password


class OnedriveDB(Base):
    __tablename__ = "onedrive"
    user_id = Column(String, primary_key=True)
    current_token = Column(String)
    refresh_token = Column(String)

    def __init__(self, user_id, current_token, refresh_token):
        self.user_id = user_id
        self.current_token = current_token
        self.refresh_token = refresh_token
