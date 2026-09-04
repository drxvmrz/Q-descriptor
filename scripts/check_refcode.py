###############################################################################
#
# This script checks if a REFCODEs in database
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

DATABASE_FILE_URL = r"https://raw.githubusercontent.com/drxvmrz/Q-descriptor/refs/heads/main/database/database.txt"

# CLASSES ######################################################################

class Settings:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Scan 'database.txt' for input refcodes")
        # non-options
        self.parser.add_argument("refcodes", nargs="+", type=str, help="The one or many refcodes to scan")
        self.refcode_list = []

    def is_valid_args(self):
        for code in self.refcode_list:
            if len(code) != 6: return False
        return True

    def parse_args(self):
        args = self.parser.parse_args()
        self.refcode_list = args.refcodes

# FUNCTIONS ####################################################################

def check_ref_in_database(settings : Settings):
    pass

# MAIN #########################################################################

def main():
    sets = Settings()
    sets.parse_args()

    if not sets.is_valid_args():
        print("ERROR! Invalid REFCODE")
        exit(1)


main()