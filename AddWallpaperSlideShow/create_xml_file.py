#!/usr/bin/env python3

from imghdr import what
from os import getuid
from os import listdir
from os import makedirs
from os import path
from random import random
from sys import argv
from sys import stderr

static_tag_structure = """
  <static>
    <duration>%.2f</duration>
    <file>%s</file>
  </static>"""

transition_tag_structure = """
  <transition>
    <duration>%.2f</duration>
    <from>%s</from>
    <to>%s</to>
  </transition>"""

xml_file_structure = """
<background>
  <starttime>
    <year>2009</year>
    <month>08</month>
    <day>04</day>
    <hour>00</hour>
    <minute>00</minute>
    <second>00</second>
  </starttime>
<!-- This animation will start at midnight. -->{}
</background>
"""

local_dir = "~/.local/share/backgrounds/contest/"
global_dir = "/usr/share/backgrounds/contest/"
destination_dir = ""


def exit_with_error(error):
    print(error, file=stderr)
    exit(1)


def random_time_generator(min_interval, max_interval):
    def func():
        return min_interval + (max_interval - min_interval) * random()

    return func


def fixed_time_generator(time):
    def func():
        return time

    return func


def process_directory(directory):
    abs_dir_path = path.abspath(directory)
    dir_name = abs_dir_path[abs_dir_path.rindex("/") + 1:]
    return abs_dir_path + "/", dir_name


def create_xml_file(directory):
    # prompt user for wallpaper time interval mode
    print("\n------------------------------")
    print("         " + directory.upper())
    print("Please choose an option for wallpaper time:\n"
          "    1. Random interval"
          "    2. Fixed interval")
    option = None
    while option != "1" and option != "2":
        option = input("Enter option: ")

    # random interval
    if option == "1":
        min_interval = float(input("Enter minimum interval (in seconds, with or without decimal): "))
        max_interval = float(input("Enter maximum interval (in seconds, with or without decimal): "))
        get_time = random_time_generator(min_interval, max_interval)
    else:  # fixed interval
        time = input("Enter fixed interval (in seconds, with or without decimal): ")
        get_time = fixed_time_generator(time)

    # get transition time
    transition_time = float(input("Enter transition time (in seconds, with or without decimal, 1-5s is recommend): "))

    # get absolute directory path
    directory_path, directory_name = process_directory(directory)
    xml_file_name = directory_name + "-slideshow.xml"

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
    files = list(files - not_image_files)

    # create xml file content
    slideshow_tags = []
    for i in range(len(files)):
        static_tag = static_tag_structure % (
            get_time(),
            directory_path + files[i - 1]
        )
        transition_tag = transition_tag_structure % (
            transition_time,
            directory_path + files[i - 1],
            directory_path + files[i]
        )
        slideshow_tags.append(static_tag + transition_tag)

    xml_file_content = xml_file_structure.format("".join(slideshow_tags)).strip()

    # check if xml exist
    xml_abs_path = path.expanduser(destination_dir + xml_file_name)
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
    print("{} is created at {} with {} image(s)".format(xml_file_name, xml_abs_path, len(files)))


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
            exit_with_error("This script must be run as super user to create global slideshow!")
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

    # print guidance
    print("\nNow you can go to gnome-tweak -> appearance -> background/lockscreen image and choose the xml file")
