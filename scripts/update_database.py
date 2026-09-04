###############################################################################
#
# This script scans a specified folder 
# to update 'database.txt' file
#
# INITS ########################################################################

__version__ = "1.0.0"
__author__ = "Pavel D. Drozhilkin"
__email__ = "pddrozhilkin@yandex.ru"

# IMPORTS ######################################################################

import os
import sys
import argparse

# GLOBAL CONSTANTS #############################################################

DATABASE_REPO_PATH = os.path.normpath(os.path.join("..", "database", "database.txt"))

# CLASSES ######################################################################

class Settings:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="This script scans a specified folder to update 'database.txt' file")
        # non-options
        self.parser.add_argument("good_cifs_dir", type=str, help="Path to the folder contains .cif-files meets the Q-criteria")
        # options
        self.parser.add_argument("-db", "--database", type=str, default=f"{os.path.abspath(DATABASE_REPO_PATH)}", help="Path to file 'database.txt'")

        self.good_cifs_dir = ""
        self.database_path = ""

    def is_valid_args(self):
        return os.path.exists(self.good_cifs_dir) and os.path.exists(self.database_patha)

    def parse_args(self):
        args = self.parser.parse_args()

        self.good_cifs_dir = args.good_cifs_dir
        self.database_path = args.database

class Database:
    def __init__(self):
        self.current_ver_refs = []
        self.good_cif_dir_refs = []

    def download_last_ver(self):
        pass

    def get_new_refcodes(self):
        pass

    def update(self):
        pass

# MAIN #########################################################################

def main():
    pass

main()