import os
import base64
from PIL import Image, ImageOps
import io


def scan_for_new_images():
    image_group_list = []
    try:
        with os.scandir(os.getcwd() + "/images") as it:
            for entry in it:
                dir_info = {
                    "dir_name": entry.name,
                    "image_list": []
                }
                with os.scandir(entry.path) as group_dir:
                    image_list = []
                    for file in group_dir:
                        if file.name != "title.txt":
                            image_list.append(file.name)
                dir_info["image_list"] = image_list
                image_group_list.append(dir_info)
    except Exception:
        pass

    return image_group_list


def validate_image_path_and_get_converted_data(image_group_list, selected_group, current_group):
    with os.scandir(os.getcwd() + "/images") as it:
        group_found_dict = {}
        for key in image_group_list:
            group_found_dict[key] = 1
        all_group_data = {}
        for entry in it:
            if group_found_dict.get(entry.name) is not None:
                image_found_dict = {}
                for image_name_from_frontend in image_group_list[entry.name]:
                    image_found_dict[image_name_from_frontend] = 1
                folder_data = {}

                with os.scandir(entry.path) as images:
                    try:
                        with open(entry.path + "/title.txt", "r") as f:
                            title = f.read()
                    except FileNotFoundError:
                        title = "Nature Is Beautiful"
                    image_id = 1
                    image_data_dict = {
                        "title": title,
                        "image_name": None,
                        "high_res_image": None,
                        "low_res_image": None
                    }
                    for image in images:
                        if image_found_dict.get(image.name) is not None:
                            image_data_dict["image_name"] = image.name
                            image_data_dict["low_res_image"] = convert_image_into_base64(image.path,
                                                                                         full_resolution=False)
                            image_data_dict["high_res_image"] = convert_image_into_base64(image.path,
                                                                                          full_resolution=True)
                            folder_data[image_id] = image_data_dict.copy()
                            folder_data["folder_name"] = entry.name
                            image_id += 1
                if selected_group[entry.name]["selectedGroup"] == -1:
                    all_group_data[current_group] = folder_data
                    current_group += 1
                else:
                    all_group_data[selected_group[entry.name]["selectedGroup"]] = folder_data
        return all_group_data


def change_image_resolution(image_path, target_width, target_height):
    im = Image.open(image_path)
    fixed_image = ImageOps.exif_transpose(im)
    im_resize = fixed_image.resize((target_width, target_height))
    buf = io.BytesIO()
    im_resize.save(buf, format=im.format)
    byte_im = buf.getvalue()
    return byte_im


def convert_image_into_base64(image_path, full_resolution=False):
    image_obj = None
    if not full_resolution:
        image = change_image_resolution(image_path, 180, 115)
    else:
        image_obj = open(image_path, "rb")
        image = image_obj.read()
    ext = image_path.split('.')[-1]
    encoded = base64.b64encode(image).decode('ascii')
    base64_image_data = 'data:image/{};base64,{}'.format(ext, encoded)
    if full_resolution:
        image_obj.close()
    return base64_image_data


def get_string_image_from_specific_path_list(image_db_list, first_image_only=True):
    string_image_list = []
    for image_info in image_db_list:

        for image_path in os.scandir(image_info[1]):
            if image_path.name != "title.txt":
                string_image_list.append({
                    "imageID": image_path.name.split("@")[0],
                    "group": image_info[0],
                    "image": convert_image_into_base64(image_path.path, full_resolution=False)
                })
            if first_image_only:
                break
    return string_image_list


def get_one_full_res_image(image_info, image_id):
    string_image_dict = {
        "title": None,
        "imageID": None,
        "group": None,
        "image": None
    }
    for image_path in os.scandir(image_info[1]):
        if image_path.name.split("@")[0] == image_id:
            try:
                with open(image_info[1] + "\\title.txt") as f:
                    title = f.read()
            except FileNotFoundError:
                title = "Nature Is Beautiful"
            string_image_dict["title"] = title
            string_image_dict["imageID"] = image_path.name.split("@")[0]
            string_image_dict["group"] = image_info[0]
            string_image_dict["image"] = convert_image_into_base64(image_path.path, full_resolution=True)
            break
    return string_image_dict
