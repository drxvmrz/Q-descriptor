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
import urllib.request
import urllib.error
import argparse

# GLOBAL CONSTANTS #############################################################

DATABASE_FILE_URL = r"https://raw.githubusercontent.com/drxvmrz/Q-descriptor/refs/heads/main/database/database.txt"

# CLASSES ######################################################################

class Settings:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Scan 'database.txt' for input refcodes")
        # non-options
        self.parser.add_argument("refcodes", nargs="+", type=str, help="The one or many refcodes to scan")
        self.refcode_list : list[str] = []

    def is_valid_args(self):
        for code in self.refcode_list:
            if len(code) != 6: return False
        return True

    def parse_args(self):
        args = self.parser.parse_args()
        self.refcode_list = args.refcodes

class Checker:
    def __init__(self):
        self.database : list[str] = []
        self.search_status = dict()

    def output_search_stat(self):
        if len(self.database) == 0: return

        print("Search results! Check on DSC or XRD if \033[32mTrue\033[0m")
        for key in self.search_status:
            if self.search_status[key]:
                print(f"{key}: \033[32mTrue\033[0m")
            else:
                print(f"{key}: \033[31mFalse\033[0m")

    def check_refs_in_db(self, ref_to_search_list):
        if len(self.database) == 0: return

        for ref in ref_to_search_list:
            self.search_status[ref] = (ref in self.database)

    def download_db(self):
        try:
            # Открываем соединение
            with urllib.request.urlopen(DATABASE_FILE_URL) as response:
                # Читаем байты и декодируем в UTF-8
                html = response.read().decode('utf-8')
                self.database = html.split(",")
                
                print(f"Database has been download succesfully!")
                return html
                 
        except urllib.error.HTTPError as e:
            print(f"Connection Error! {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            print(f"Connection Error! {e.reason}")
        except Exception as e:
            print(f"Unknown Error! {e}")

# MAIN #########################################################################

def main():
    sets = Settings()
    sets.parse_args()

    if not sets.is_valid_args():
        print("ERROR! Invalid REFCODE")
        exit(1)

    checker = Checker()
    checker.download_db()
    checker.check_refs_in_db(sets.refcode_list)
    checker.output_search_stat()

main()