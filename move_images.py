import shutil
import os

# Description: This file contains the path of the source and destination folder
FROM = 'JPG'
TO = 'output'

# Functions: 

# utlitiy functions
def get_id(file_name, type):
    if(type == "image"):
        return file_name.split('_')[4].split('.')[0][:-3]
    return file_name[-10:]


# main functions
# Description: This function moves the images from the source folder to the destination folder
def move():
    # get the id from the folders inside FROM folder
    for folder in os.listdir(FROM):
        # get the id from the images inside the folder
        for file in os.listdir(os.path.join(FROM, folder)):
            image_id = get_id(file, "image")

            # now in TO folder we have to find a folder with the same id in its name
            for parent_folder in [folder for folder in os.listdir(TO) if os.path.isdir(os.path.join(TO, folder))]:
                for main_folder in os.listdir(os.path.join(TO, parent_folder)):
                    if("original" not in main_folder):
                        folder_id = get_id(main_folder, "folder")
                        if(image_id == folder_id):
                            print("image file " + file)
                            # instead of copying the file i want to move it
                            shutil.move(os.path.join(FROM, folder, file), os.path.join(TO, parent_folder, main_folder, "images"))
            

if __name__ == '__main__':
    move()