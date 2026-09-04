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
    def __init__(self, settings : Settings):
        self.settings = settings
        self.current_ver_refs = set()
        self.good_cif_dir_refs = set()

    def load_last_ver(self):
        with open(DATABASE_REPO_PATH, "r") as f:
            str_arr = f.read().split(",")
            self.current_ver_refs = set(str_arr)

    def get_refcodes_from_cif_dir(self):
        for root, dirs, files in os.walk(DATABASE_REPO_PATH):
            if root != DATABASE_REPO_PATH: continue
            self.current_ver_refs = set(files)

    def update(self):
        diff_set = self.good_cif_dir_refs.difference(self.current_ver_refs)

        if len(diff_set) == 0: 
            print(f"Database is up to date with respect to {self.settings.good_cifs_dir}")
            return

        diff_list = list(diff_set)

        with open(DATABASE_REPO_PATH, "a") as f:
            for ref in diff_list:
                f.write(f"{ref}, ")

        print(f"Database has been updated with respect to {self.settings.good_cifs_dir}")


# MAIN #########################################################################

def main():
    settings = Settings()
    settings.parse_args()

    dbase = Database(settings)
    dbase.load_last_ver()
    dbase.get_refcodes_from_cif_dir()
    dbase.update()


main()