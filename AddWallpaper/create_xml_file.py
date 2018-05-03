#!/usr/bin/env python3

from imghdr import what
from os import getuid
from os import listdir
from os import makedirs
from os import path
from sys import argv
from sys import stderr

wallpaper_tag_structure = """
 <wallpaper>
      <name>{name}</name>
      <filename>{filename}</filename>
      <options>zoom</options>
      <pcolor>#000000</pcolor>
      <scolor>#000000</scolor>
      <shade_type>solid</shade_type>
 </wallpaper>"""

xml_file_structure = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE wallpapers SYSTEM "gnome-wp-list.dtd">
<wallpapers>{}
</wallpapers>
"""

destination_dir = ""
global_dir = "/usr/share/gnome-background-properties/"
local_dir = "~/.local/share/gnome-background-properties/"


def exit_with_error(error):
    print(error, file=stderr)
    exit(1)


def remove_filename_extension(filename):
    return filename[:filename.rindex(".")]


def process_directory(directory):
    abs_dir_path = path.abspath(directory)
    dir_name = abs_dir_path[abs_dir_path.rindex("/") + 1:]
    return abs_dir_path + "/", dir_name


def create_xml_file(directory):
    # get absolute directory path
    directory_path, directory_name = process_directory(directory)
    xml_file_name = directory_name + "-wallpapers.xml"

    # get image files in directory
    files = set(listdir(directory_path))
    not_image_files = set()
    for file in files:
        if what(directory_path + file) is None:
            not_image_files.add(file)
    if len(not_image_files) > 0:
        print("In directory {}, these files are not images and will be ignored:".format(directory_name))
        for t in not_image_files:
            print("  " + t)
        print("\n")
    files = files - not_image_files

    # create xml file content
    wallpaper_tags = []
    for file in files:
        wallpaper_tags.append(wallpaper_tag_structure.format(
            name=remove_filename_extension(file),
            filename=directory_path + file
        ))
    xml_file_content = xml_file_structure.format("".join(wallpaper_tags)).strip()

    # check if xml exist
    xml_abs_path = destination_dir + xml_file_name
    if path.isfile(xml_abs_path):
        print("File {} has already exist".format(xml_file_name))
        option = ""
        while option.upper() not in ("YES", "NO", "Y", "N"):
            option = input("Do you want to overwrite it? (y/n) ")
        if option.upper() in ("NO", "N"):
            exit_with_error("User abortion")

    # create xml file
    try:
        f = open(xml_abs_path, "w+")
        f.write(xml_file_content)
        f.close()
    except FileNotFoundError:
        exit_with_error("Invalid file path: " + xml_abs_path)
    except PermissionError:
        exit_with_error("Permission error occurred")
    except IOError:
        exit_with_error("Cannot create file " + xml_abs_path)

    # output result for user
    print("{} is created at {} with {} image(s)".format(xml_file_name, destination_dir, len(files)))


if __name__ == '__main__':
    # check number of parameters
    if len(argv) == 1:
        exit_with_error("Please pass at least one directory name")

    # choose global or local
    option = ""
    while option not in ["G", "L", "GLOBAL", "LOCAL"]:
        option = input("Add wallpaper globally or locally? (G/L) ").upper()

    # choose destination dir accordingly
    if option in ["G", "GLOBAL"]:
        # check for sudo
        if getuid() != 0:
            exit_with_error("This script must be run as super user to create global wallpapers!")
        destination_dir = global_dir
    else:
        local_dir = path.expanduser(local_dir)
        makedirs(local_dir, exist_ok=True)  # create directories
        destination_dir = local_dir

    # remove invalid directory
    invalid_arg = set([d for d in argv[1:] if not path.isdir(d)])
    if len(invalid_arg) > 0:
        print("Followings are invalid directory name(s) and will be ignored:")
        for t in invalid_arg:
            print("  " + t)
        print("\n")

    # create xml files
    for directory in argv[1:]:
        create_xml_file(directory)
