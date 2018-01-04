#!/usr/bin/env python3

from imghdr import what
from os import listdir
from os.path import abspath
from os.path import isfile
from sys import argv

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

destination_dir = "/usr/share/gnome-background-properties/"


def exit_with_error(error):
    print(error)
    exit(1)


def remove_filename_extension(filename):
    return filename[:filename.rindex(".")]


def process_directory(directory):
    abs_dir_path = abspath(directory)
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
    if isfile(xml_abs_path):
        print("File {} has already exist".format(xml_abs_path))
        option = ""
        while option.upper() not in ("YES", "NO", "Y", "N"):
            option = input("Do you want to overwrite it? (y/n) ")
        if option.upper() in ("NO", "N"):
            exit_with_error("User abortion")

    # create xml file at /usr/share/gnome-background-properties
    try:
        f = open(xml_abs_path, "w")
        f.write(xml_file_content)
        f.close()
    except FileNotFoundError:
        exit_with_error("Invalid file path")
    except PermissionError:
        exit_with_error("Please run this script as root")
    except IOError:
        exit_with_error("Cannot create file {}".format(xml_abs_path))


if __name__ == '__main__':
    if len(argv) == 1:
        exit_with_error("Please pass at least one directory name")

    for directory in argv[1:]:
        create_xml_file(directory)