import shutil
import os
from rich import print as rprint

# Description: This file contains the path of the source and destination folder
FROM = 'testing\JPG'
TO = 'testing\output'

# Functions: 

# utlitiy functions
def get_id(file_name, type):
    if(type == "image"):
        # return file_name.split('_')[4].split('.')[0][:-5]
        idx = file_name.find('_ID_')
        return file_name[idx + 4:idx + 14]
    return file_name[-10:]


# main functions
# Description: This function moves the images from the source folder to the destination folder
def move():
    # get the id from the folders inside FROM folder
    for folder in os.listdir(FROM):
        # get the id from the images inside the folder
        for file in os.listdir(os.path.join(FROM, folder)):
            rprint(f"[bold magenta] Reading image file: {file} [/bold magenta]")
            image_id = get_id(file, "image")
            rprint(f"[green]ID of this file : {image_id}[/green]")

            # now in TO folder we have to find a folder with the same id in its name
            rprint(f"[blue] Now searching matching folder in {TO} directory...[/blue]")
            for parent_folder in [folder for folder in os.listdir(TO) if (os.path.isdir(os.path.join(TO, folder)))]:
                if(parent_folder == 'A4'):
                    continue
                else:
                    for main_folder in os.listdir(os.path.join(TO, parent_folder)):
                        if("original" not in main_folder):
                            folder_id = get_id(main_folder, "folder")
                            rprint(f"[yellow]Folder name: {main_folder}[/yellow]")
                            rprint(f"[green]ID: {folder_id}[/green]")
                            if(image_id == folder_id):
                                rprint(f"[grey] ID matched ✅[/grey]")
                                rprint("[orange]Moving image to this folder...[/orange]")
                                # instead of copying the file i want to move it
                                shutil.move(os.path.join(FROM, folder, file), os.path.join(TO, parent_folder, main_folder, "images"))
                                break
                            else:
                                rprint(f"[red] ID didn't matched ❌[/red]")

                            rprint("-" * 80) # ending line to differentiate

if __name__ == '__main__':
    move()