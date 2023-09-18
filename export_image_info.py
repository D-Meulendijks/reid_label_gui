import json
import os
import shutil

class ImageInfoExporter():

    def __init__(self):
        self.image_info_path = "./image_info.json"
        self.export_folder_path = "./exported_data"

    def load_image_info(self):
        try:
            # Load image info (click status and folder name for each column) from a JSON file
            with open("image_info.json", "r") as json_file:
                self.image_info = json.load(json_file)
        except FileNotFoundError:
            # Initialize image info with default values if the file doesn't exist
            self.image_info = {str(self.current_anchor_id):{'image_name':[], 'image_folder':[]}}

    def export_image_info(self):
        if not os.path.exists(self.export_folder_path):
            os.mkdir(self.export_folder_path)
        for image_info_key in self.image_info:
            sub_folder_path = os.path.join(self.export_folder_path, image_info_key)
            if not os.path.exists(sub_folder_path):
                os.mkdir(sub_folder_path)
            self.export_image_paths(self.image_info[image_info_key], image_info_key)

    def export_image_paths(self, image_infos, image_info_key):
        image_folders = image_infos['image_folder']
        image_names = image_infos['image_name']
        for image_folder, image_name in zip(image_folders, image_names):
            image_path = os.path.join(image_folder, image_name)
            export_path = os.path.join(self.export_folder_path, f"{image_info_key}/", image_name)
            shutil.copyfile(image_path, export_path)



if __name__ == "__main__":
    exporter = ImageInfoExporter()
    exporter.load_image_info()
    exporter.export_image_info()