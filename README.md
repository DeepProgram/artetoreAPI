
# Artetore ImageHub API

Backend Of Artetore Frontend


## Frontend
Setup the frontend to visualize data properly

[Artetore](https://github.com/DeepProgram/artetore)
## Environment Variables

To run this project, you will need to add the following environment variables to your **.env**  file

    db_username = demo_username
    db_password = demo_password
    host = demo_mysql_database_host
    port = demo_mysql_database_port
    folder_arts_id = demo_ondedrive_root_folder_id
    client_secret = demo_onedrive_client_secret
    client_id = demo_onedrive_client_id


## Features
-
    ### Router [ /login ]
    - Takes username and password as query and validate with database and returns JWT token if successful

-
    ### Router [ /image ]
    - **get_whole_page_image** function takes page number as query input and returns that page image list if available in database
    - **get_group_image** function takes group number as input and returns image list of that group
    - **get_single_image** function takes group, image_id as query input and returns a sigle high resolution image
    - **total-page** functon returns total page number taht can be generated by counting all image group from database

-
    ### Router [ /admin ]
    - **onedrive_connection** accepts JWT token as input and returns if onedrive connection is successful or not
    - **onedrive_folders** accepts JWT token as input and returns folder list of onedrive **folder_arts_id [ Added on .env ]** folder list 
    - **rename_operation** taskes input of item_id, new_name, JWT and returrn result of operation
    - **add_folder_operation** taskes input of folder_name, JWT and returrn result of operation
    - **folder_delete_operation** taskes input of folder_id, JWT and returrn result of operation
    - **file_upload_session** taskes input of folder_id, file_name, JWT and returns onedrive session url to upload on that specific folder
    - **groups** returns only group list from database
    - **add_image_in_database_operation** takes image_list, JWT token as input and return operation status 
        ```json
        {
        "image_list":{
            "01TX4ZA735SY5SYKPEY5HJ7XW6CC2FUBRY": {
                "all_image_id": [
                    {
                        "file_name": "steps-in-instruction-execution-by-cpu.png",
                        "file_id": "01TX4ZA77HMAJQR72NJZC2ZNJEZEK22ILO"
                        }
                    ]
                    ,
                    "group": -1,
                    "folder_name": "System"
                }
            }
        }
    - **delete_image_in_database_operation** takes image_list, JWT token as input and return operation status
        ```
        {
            "image_list":{
                "17": [
                    {
                        "folder_name": "System",
                        "image_id": 1,
                        "image_name":"steps-in-instruction-execution-by-cpu.png"
                    }
                ]
            }
        }
    - **get_single_image_from_group** takes group_id, image_id, JWT token and returns low resolution image
    - **get_groups_with_images** takes JWt token as input and returns all group lsit with images

## Screenshots
One Page Image List

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/2-whole_page_image.png)


One Group Image List

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/4-group_image_list.png)


High Resolution Image

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/3-high_res_image.png)

Total Page

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/5-total_page.png)

Download Full Resolution Image

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/6-download_image.png)

Admin Login

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/1-admin_login.png)

Connect Onedrive

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/7-connect_onedrive.png)

Onedrive Folders

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/8-onedrive_folders.png)

Rename Item

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/9-rename_item.png)

Create New Folder

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/10-add_folder.png)

Delete Folder

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/11-delete_folder.png)

Database Group List

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/12-database_groups_list.png)

Add Image In Database

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/13-add_image_in_db.png)

Database Groups With Images

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/14-db_groups_with_image_info.png)

Delete Image From Database

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/15-delete_image_from_db.png)

Low Resolution Image

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/16-low_res_image.png)

Database ImageDB Schema

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/17-database_imagedb_schema.png)

Database Onedrive Schema

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/19-database_onedrive_schema.png)

Database UserDB Schema

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/20-database_userdb_schema.png)

Database UserDB Data

![App Screenshot](https://raw.githubusercontent.com/DeepProgram/artetoreAPI/screenshot/screenshot/21-database_userdb_data.png)
