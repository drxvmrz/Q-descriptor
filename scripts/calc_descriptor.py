###############################################################################
#
# This script searches in specified folder contains .cif-files 
# of monoclinic crystals from the CCDC-2023 database that 
# may undergo a monoclinic-to-orthorhombic structural phase transition.
# 
# First, the possibility of constructing an orthorhombic supergroup-basis
# in the initial monoclinic crystal basis is checked. Then, pseudosymmetry 
# is checked with respect to the reflection planes and two-fold axes defined 
# along new orthorhombic translations with a specified spatial orientation error.
#
# To run this script APEXSYMM must be installed on your PC:
# https://github.com/drxvmrz/apexsymm
#
# INITS ########################################################################

__version__ = "1.0.0"
__author__ = "Pavel D. Drozhilkin"
__email__ = "pddrozhilkin@yandex.ru"

# IMPORTS ######################################################################

import os
import sys
import json
import copy
import argparse
import numpy as np
import subprocess as sb

from math import *

# GLOBAL CONSTANTS #############################################################

SETUP_BETA = 0 # Unique axis 'b'
SETUP_GAMMA = 1 # Unique axis 'c'

# CLASSES ######################################################################

class AppSettings:
    """
    App settings and CLI-parsing here
    """
    def __init__(self, cif_path, json_drop_path, cif_drop_path, q_threshold, ntot_threshold, nsublmax_threshold, nsublmin_threshold, ang_error, ang_step, border_int, apex_path):
        self.cif_folder_path = cif_path

        self.json_drop_folder_path = json_drop_path
        self.cif_drop_folder_path = cif_drop_path

        self.q_descr_upper_threshold = q_threshold
        self.ntot_threshold = ntot_threshold
        self.nsmax_threshold = nsublmax_threshold
        self.nsmin_threshold = nsublmin_threshold

        self.angle_error = ang_error
        self.angle_step = ang_step
    
        self.border_int = border_int

        self.apexcore_path = apex_path

    @staticmethod
    def parse_cli():
        parser = argparse.ArgumentParser("Pseudosymmetry calcs based on Q-descriptor values", 
                                        description="Calcs Q-descriptor and then pseudosymm with respect to only reliable operators!")
        # non-optionals
        parser.add_argument("init_dir", type=str, help="Path to the folder contains .cif-files")

        # optionals
        parser.add_argument("-oj", "--out_jsons", type=str, default=f"{os.path.dirname(__file__)}", help="Path to the folder for dumping json-files with apexsymm calculations results")
        parser.add_argument("-oc", "--out_cif", type=str, default=f"{os.path.dirname(__file__)}", help="Path to the folder for dumping cif-files that meets the value criteria")

        parser.add_argument("-qt", "--qthreshold", type=float, default=0.052, help="Threshold for Q-descritpor value to accept structure for calcs")
        parser.add_argument("-ntott", "--ntot_threshold", type=float, default=0.225, help="Threshold for n_tot value to accept structure as pseudosymmetric")
        parser.add_argument("-nsmat", "--nsublmax_threshold", type=float, default=0.353, help="Threshold for n_subl.max value to accept structure as pseudosymmetric")
        parser.add_argument("-nsmit", "--nsublmin_threshold", type=float, default=0.020, help="Threshold for n_subl.min value to accept structure as pseudosymmetric")

        parser.add_argument("-ae", "--angerr", type=int, default=3, help="Angle orientation error for pseudosymmetry operator")
        parser.add_argument("-as", "--angstep", type=int, default=1, help="Angle orientation step")
        parser.add_argument("-mn", "--max_int", type=int, default=2, help="Max value {m, n, p, q} values as abs. The calculations range will be constructed as [-max_int; max_int]")

        default_apex_path = ""
        if sys.platform == "win32" or sys.platform == "win64":
            default_apex_path = r"C:\Program Files\Apexsymm\core\apexcore_win.exe"
        elif sys.platform == "darwin" or sys.platform == "mac": 
            default_apex_path = r"/Applications/Apexsymm.app/Contents/MacOS/core/apexcore_mac"
        else:
            default_apex_path = ""

        parser.add_argument("-ap", "--apexpath", type=str, default=default_apex_path, 
                            help="Enter the path to Apexsymm core execution file 'apexcore(.exe)'")

        cmd = parser.parse_args()

        aim_dir = cmd.init_dir
        out_jsons_dir = cmd.out_jsons
        out_cif_dir = cmd.out_cif
        q_upper_thresh = cmd.qthreshold
        ntot_low_thresh = cmd.ntot_threshold
        nsmax_low_thresh = cmd.nsublmax_threshold
        nsmin_low_thresh = cmd.nsublmin_threshold
        angle_err = cmd.angerr
        angle_step = cmd.angstep
        max_int = cmd.max_int
        apex_path = cmd.apexpath

        # Returns AppSettings object without any validation at first
        return AppSettings(aim_dir, out_jsons_dir, out_cif_dir, q_upper_thresh, ntot_low_thresh, nsmax_low_thresh, nsmin_low_thresh, angle_err, angle_step, max_int, apex_path)

    def is_valid(self):
        valid = True
        
        # Main calc directory contains cif-files to calc
        if not os.path.isdir(self.cif_folder_path): 
            print("FATAL ERROR! Entered .cif-folder path is not dir path")
            valid = False
        if not os.path.exists(self.cif_folder_path):
            print("FATAL ERROR! Entered .cif-folder path does not exists")
            valid = False

        # Directory to drop good cifs of structures (meets the criteria)
        if self.cif_drop_folder_path != "":
            if not os.path.isdir(self.cif_drop_folder_path): 
                print("FATAL ERROR! Entered .cif drop folder path is not dir path")
                valid = False
            if not os.path.exists(self.cif_drop_folder_path):
                print("FATAL ERROR! Entered .cif drop folder path does not exists")
                valid = False
        
        # Directory to drop .cif files of structures (meets the criteria) 
        if self.json_drop_folder_path != "":
            if not os.path.isdir(self.json_drop_folder_path): 
                print("FATAL ERROR! Entered .json drop folder path is not dir path")
                valid = False
            if not os.path.exists(self.json_drop_folder_path):
                print("FATAL ERROR! Entered .json drop folder path does not exists")
                valid = False

        # Q-descriptor upper threshold (lower is always 0.0)
        if self.q_descr_upper_threshold < 0:
            print("FATAL ERROR! Wrong Q-descriptor threshold value!")
            valid = False
        if self.q_descr_upper_threshold > 1:
            print("FATAL ERROR! Q-descriptor value cannot be more than 1!")
            valid = False

        # Pseudosymmetry 'n' value lower threshold
        if self.ntot_threshold < 0 or self.ntot_threshold > 1:
            print("FATAL ERROR! Pseudosymmetry degree of invariance value can be only from 0 to 1!")
            valid = False
        if self.nsmax_threshold < 0 or self.nsmax_threshold > 1:
            print("FATAL ERROR! Pseudosymmetry degree of invariance value can be only from 0 to 1!")
            valid = False
        if self.nsmin_threshold < 0 or self.nsmin_threshold > 1:
            print("FATAL ERROR! Pseudosymmetry degree of invariance value can be only from 0 to 1!")
            valid = False

        # Error of orientation angle of pseudosymmetry operators!
        if self.angle_error < 0: 
            print("FATAL ERROR! Angle error should be an INTEGER and more than zero!")
            valid = False

        # {m,n,p,q}-coeffs values
        if self.border_int <= 0:
            print("FATAL ERROR! {m,n,p,q} values can be only positive INTEGERS")
            valid = False

        # Apexsymm core path
        if not os.path.exists(self.apexcore_path):
            print(f"FATAL ERROR! Apesymm core execution file not found on {self.apexcore_path}")
            print("Please try to reinstall 'Apexsymm' on this path or enter your own but correct one!")
            valid = False
        
        return valid 


class ApprovedDescriptor:
    """
    Fours of numbers m, n, p, q that are suitable for constructing a orthorhombic basis
    """
    def __init__(self, m: float, n: float, p: float, q: float):
        self.m = m
        self.n = n
        self.p = p
        self.q = q


class OperatorBlock:
    def __init__(self):
        self.u_trans_affine: str = ""
        self.v_trans_affine: str = ""
        self.axes_and_planes: str = "" 


class MonoclinicCrystal:
    def __init__(self, a, b, c, beta, gamma, primary_cif_path: str, cell_setup):
        # CCDC REFCODE of crystal
        self.refcode = os.path.basename(primary_cif_path)[:6]

        # current structure .cif-files pathways
        self.primary_cif = primary_cif_path # Whole structure .cif-file path
        self.atoms_cifs : list[str] = [] # Atom sublattices .cif-file paths

        # Cell parameters (read from .cif-file of whole structure)
        self.a = a
        self.b = b
        self.c = c
        self.alpha = 90
        self.beta = beta
        self.gamma = gamma
        self.cell_setup = cell_setup

        # The matrix contains initial translations in cartesian basis
        self.cart_matrix = None

        # Array of maximal values of 'eta' for atoms sublattices
        # It stored like that: [[('eta' for found translations), maximal 'eta' from axes and mirror planes], [...//...]]
        #                        |--------------------- .cif file for atom sublattice  -------------------|
        # for current operators blocks
        self.current_n_subl_max_arr : list[list[tuple[float] | float]] = []

    def create_cart_matrix(self):
        """
        Returns the matrix contains coords of inital translations in cartesian basis

        It seems like:
        [x_a, y_a, z_a] <- a = (x, y, z)
        [x_b, y_b, z_b] <- b = (x, y, z)
        [x_c, y_c, z_c] <- c = (x, y, z)
        """
        a = self.a
        b = self.b
        c = self.c

        sin_gamma = sin(radians(self.gamma))
        cos_alpha = cos(radians(self.alpha))
        cos_beta = cos(radians(self.beta))
        cos_gamma = cos(radians(self.gamma))

        xi = sqrt(1 - cos_alpha * cos_alpha - cos_beta * cos_beta - cos_gamma * cos_gamma + 2 * cos_beta * cos_gamma * cos_alpha)

        a11 = 1 / (a * sin_gamma)
        a12 = 0
        a13 = -(cos_beta - cos_gamma * cos_alpha) / (a * xi * sin_gamma)
        a21 = -cos_gamma / (b * sin_gamma)
        a22 = 1 / b
        a23 = -(1 / (b * xi)) * (sin_gamma * cos_alpha - cos_gamma * (cos_beta - cos_gamma * cos_alpha) / sin_gamma)
        a31 = 0
        a32 = 0
        a33 = sin_gamma / (c * xi)

        a_matrix = np.array([[a11, a12, a13],
                             [a21, a22, a23],
                             [a31, a32, a33]])

        b_matrix = np.array([[1.0, 0.0, 0.0],
                             [0.0, 1.0, 0.0], 
                             [0.0, 0.0, 1.0]])

        self.cart_matrix = np.linalg.solve(np.transpose(a_matrix), b_matrix)

    def _vec_to_cart(self, vec_affine):
        return np.matmul(np.transpose(self.cart_matrix), vec_affine)

    def _vec_to_affine(self, vec_cart):
        return np.matmul(np.linalg.inv(np.transpose(self.cart_matrix)), vec_cart)

    @staticmethod
    def _get_2_fold_axis(cell_setup, mono_plane_angle):
        """
        Returns the marix of 2 fold axes oriented in moniclinic plane
        makes an angle 'mono_plane_angle' with the axis 'a'
        """
        # rotation angle is 180 deg and it keeps constant
        a_cos = cos(radians(180))
        a_sin = sin(radians(180))

        x, y, z = (0.0, 0.0, 0.0)
        if cell_setup == SETUP_BETA:
            x = cos(radians(mono_plane_angle))
            y = 0
            z = sin(radians(mono_plane_angle))
        else:
            x = cos(radians(mono_plane_angle))
            y = sin(radians(mono_plane_angle))
            z = 0

        a11 = a_cos + (1 - a_cos)*x**2
        a12 = (1 - a_cos)*x*y - (a_sin)*z
        a13 = (1 - a_cos)*x*z + (a_sin)*y
        a21 = (1 - a_cos)*y*x + (a_sin)*z
        a22 = a_cos + (1 - a_cos)*y**2
        a23 = (1 - a_cos)*y*z - a_sin*x
        a31 = (1 - a_cos)*z*x - a_sin*y
        a32 = (1 - a_cos)*z*y + a_sin*x
        a33 = a_cos + (1 - a_cos)*z**2

        return [[a11, a12, a13],[a21, a22, a23],[a31, a32, a33]]

    @staticmethod
    def _get_plane(cell_setup, mono_plane_angle):
        """
        Returns the marix of mirror plane with normal oriented in moniclinic plane
        makes an angle 'mono_plane_angle' with the axis 'a'
        """
        x, y, z = (0.0, 0.0, 0.0)
        if cell_setup == SETUP_BETA:
            x = cos(radians(mono_plane_angle))
            y = 0
            z = sin(radians(mono_plane_angle))
        else:
            x = cos(radians(mono_plane_angle))
            y = sin(radians(mono_plane_angle))
            z = 0

        a11 = 1 - 2*x**2
        a12 = -2*x*y
        a13 = -2*x*z
        a21 = -2*y*x
        a22 = 1 - 2*y**2
        a23 = -2*y*z
        a31 = -2*z*x
        a32 = -2*z*y
        a33 = 1 - 2*z**2

        return [[a11, a12, a13],[a21, a22, a23],[a31, a32, a33]]
    
    def get_suitable_mnpq(self, settings: AppSettings):
        """
        Calculates Q-descriptor and collect all m, n, p, q vals 
        for which Q(m, n, p, q) < qthreshold
        """
        approved : list[ApprovedDescriptor] = []

        side = 0
        cos_mono = 0
        if self.cell_setup == SETUP_BETA:
            side = self.c
            cos_mono = cos(radians(self.beta))
        elif self.cell_setup == SETUP_GAMMA: 
            side = self.b
            cos_mono = cos(radians(self.gamma))
        else:
            print("FATAL ERROR! Unknown cell setup error!")
            exit(101)

        min_v = -settings.border_int
        max_v = settings.border_int+1

        m_arr = list(range(min_v, max_v))
        m_arr.append(0.5)
        m_arr.append(-0.5)
        m_arr.sort(reverse=True)
        n_arr = list(range(min_v, max_v))
        n_arr.append(0.5)
        n_arr.append(-0.5)
        n_arr.sort(reverse=True)
        p_arr = list(range(min_v, max_v))
        p_arr.append(0.5)
        p_arr.append(-0.5)
        p_arr.sort(reverse=True)
        q_arr = list(range(min_v, max_v))
        q_arr.append(0.5)
        q_arr.append(-0.5)
        q_arr.sort(reverse=True)

        for m in m_arr:
            for n in n_arr:
                for p in p_arr:
                    for q in q_arr:
                        if m == 0 and n == 0 and p == 0 and q == 0: continue
                        if m*q == n*p: continue
                        if m*q - n*p < 0: continue

                        # Only right vector triplets are considered
                        if self.cell_setup == SETUP_BETA and np.linalg.det(np.array([[m, 0, n],[0, 1, 0],[p, 0, q]])) < 0: continue
                        if self.cell_setup == SETUP_GAMMA and np.linalg.det(np.array([[m, n, 0], [p, q, 0], [0, 0, 1]])) < 0: continue

                        try:
                            Q_val_up = q*p*self.a**2 + n*m*side**2 - (m*q + n*p)*self.a * side * cos_mono
                            Q_val_down_left = sqrt((q*self.a - n*side)**2 + 2*q*n*self.a*side*(1-cos_mono))
                            Q_val_down_right = sqrt((p*self.a - m*side)**2 + 2*p*m*self.a*side*(1-cos_mono))
                            Q = abs(Q_val_up/(Q_val_down_left * Q_val_down_right))
                            if Q < settings.q_descr_upper_threshold: 
                                approved.append(ApprovedDescriptor(m, n, p, q))
                        except:
                            continue 

        return approved
                        
    def get_operator_to_check_blocks(self, suitable_mnpq : list[ApprovedDescriptor], settings: AppSettings):
        ops_to_check : list[OperatorBlock] = []

        for apd in suitable_mnpq:
            new_block = OperatorBlock()

            # Construct the new orthorhombic basis translations for 'apexcore'
            m, n, p, q = [apd.m, apd.n, apd.p, apd.q]
            det = (m*q-n*p)

            # Conditions that must never be met
            if m == 0 and n == 0 and p == 0 and q == 0: continue
            if m*q == n*p: continue
            if m*q - n*p < 0: continue

            vec_u_affine = None
            vec_v_affine = None
            if self.cell_setup == SETUP_BETA:
                vec_u_affine = np.array([q/det, 0, -n/det])
                vec_v_affine = np.array([-p/det, 0, m/det])
            else:
                vec_u_affine = np.array([q/det, -n/det, 0])
                vec_v_affine = np.array([-p/det, m/det, 0])
            new_block.u_trans_affine = f"1 0 0/0 1 0/0 0 1/{vec_u_affine[0]:.3f} {vec_u_affine[1]:.3f} {vec_u_affine[2]:.3f}/u_vec"
            new_block.v_trans_affine = f"1 0 0/0 1 0/0 0 1/{vec_v_affine[0]:.3f} {vec_v_affine[1]:.3f} {vec_v_affine[2]:.3f}/v_vec"

            # Construct rotation and mirror matrices for respective basis vectors (see above)
            vec_u_cart = self._vec_to_cart(vec_u_affine)
            vec_v_cart = self._vec_to_cart(vec_v_affine)
            a_cart = self.cart_matrix[0]
            
            # Initial angles between a and u/v vectors (new orthorhombic basis)
            au_dot = np.dot(a_cart, vec_u_cart)/(np.linalg.norm(vec_u_cart)*np.linalg.norm(a_cart))
            if au_dot > 1: au_dot = 1.0
            if au_dot < 1: au_dot = -1.0
            au_angle = degrees(acos(au_dot))

            av_dot = np.dot(a_cart, vec_v_cart)/(np.linalg.norm(vec_v_cart)*np.linalg.norm(a_cart))
            if av_dot > 1: av_dot = 1.0
            if av_dot < 1: av_dot = -1.0
            av_angle = degrees(acos(av_dot))

            for au in np.arange(au_angle-settings.angle_error, au_angle+settings.angle_error+1, settings.angle_step):
                npl = self._get_plane(self.cell_setup, au)
                nax = self._get_2_fold_axis(self.cell_setup, au)
                new_block.axes_and_planes += f"{npl[0][0]:.3f} {npl[0][1]:.3f} {npl[0][2]:.3f}/{npl[1][0]:.3f} {npl[1][1]:.3f} {npl[1][2]:.3f}/{npl[2][0]:.3f} {npl[2][1]:.3f} {npl[2][2]:.3f}/0 0 0/m_{au:.3f}_deg;"
                new_block.axes_and_planes += f"{nax[0][0]:.3f} {nax[0][1]:.3f} {nax[0][2]:.3f}/{nax[1][0]:.3f} {nax[1][1]:.3f} {nax[1][2]:.3f}/{nax[2][0]:.3f} {nax[2][1]:.3f} {nax[2][2]:.3f}/0 0 0/2_{au:.3f}_deg;"

            for av in np.arange(av_angle-settings.angle_error, av_angle+settings.angle_error+1, settings.angle_step):
                npl = self._get_plane(self.cell_setup, av)
                nax = self._get_2_fold_axis(self.cell_setup, av)
                new_block.axes_and_planes += f"{npl[0][0]:.3f} {npl[0][1]:.3f} {npl[0][2]:.3f}/{npl[1][0]:.3f} {npl[1][1]:.3f} {npl[1][2]:.3f}/{npl[2][0]:.3f} {npl[2][1]:.3f} {npl[2][2]:.3f}/0 0 0/m_{av:.3f}_deg;"
                new_block.axes_and_planes += f"{nax[0][0]:.3f} {nax[0][1]:.3f} {nax[0][2]:.3f}/{nax[1][0]:.3f} {nax[1][1]:.3f} {nax[1][2]:.3f}/{nax[2][0]:.3f} {nax[2][1]:.3f} {nax[2][2]:.3f}/0 0 0/2_{av:.3f}_deg;"
            
            ops_to_check.append(new_block)
        return ops_to_check

    def save_primary_cif(self, settings : AppSettings):
        """
        It makes sense to save only the .cif-file for whole structure, 
        without atom sublattices
        """
        if settings.cif_drop_folder_path == "": return

        # Saving primary cif
        cif_lines = ""
        with open(self.primary_cif, "r") as f:
            cif_lines = f.read()

        file_name = os.path.basename(self.primary_cif)
        save_path = os.path.join(settings.cif_drop_folder_path, file_name)
        with open(save_path, "w") as f:
            f.write(cif_lines)

    def delete_structure_cifs(self):
        if os.path.exists(self.primary_cif): 
            os.remove(self.primary_cif)
        
        for atom_cif in self.atoms_cifs:
            if os.path.exists(atom_cif): 
                os.remove(atom_cif) 

    def unite_structure_jsons_to_one(self, settings : AppSettings):
        """
        Unite all JSON files created while calculations by APEXSYMM 
        for a given refcode into one file.

        We take the results from '_axes.json' and '_trans.json' for primary cif and sublattices.
        Then it unites into one file named as REFCODE.json
        
        Also this function rename the primary file as a refcode. 
        Unnecessary jsons is deleted!
        """
        # If there are no JSONs, then we simply exit the function.
        if settings.json_drop_folder_path == "": return

        # We reserve '_trans.json' from the whole structure as the main .json, where we'll eventually dump everything
        prim_cif = os.path.basename(self.primary_cif)
        main_json_path = os.path.join(settings.json_drop_folder_path, prim_cif.replace(".cif", "_trans.json"))
        
        main_json_data = None
        with open(main_json_path, "r", encoding="utf-8", errors="ignore") as file:
            main_json_data = json.load(file)

        # Take operators from '_axes.json' of primary structure
        json_data = None
        with open(main_json_path.replace("_trans", "_axes"), "r", encoding="utf-8", errors="ignore") as file:
            json_data = json.load(file)
    
        operators = json_data["structures"][0]["operators"]
        main_json_data["structures"][0]["operators"].extend(operators)

        # Take operators from '_axes.json' of sublattice .cifs
        for atom_path in self.atoms_cifs:
            atom = os.path.basename(atom_path)
            
            main_atom_data = None
            main_atom_cif = os.path.join(settings.json_drop_folder_path, atom.replace(".cif", "_trans.json"))
            with open(main_atom_cif, "r", encoding="utf-8", errors="ignore") as file:
                main_atom_data = json.load(file)

            secondary_atom_data = None
            secondary_atom_cif = os.path.join(settings.json_drop_folder_path, atom.replace(".cif", "_axes.json"))
            with open(secondary_atom_cif, "r", encoding="utf-8", errors="ignore") as file:
                secondary_atom_data = json.load(file)

            secondary_operators = secondary_atom_data["structures"][0]["operators"]
            main_atom_data["structures"][0]["operators"].extend(secondary_operators)
            main_json_data["structures"].extend(main_atom_data["structures"]) 

        with open(os.path.join(settings.json_drop_folder_path, prim_cif.replace(".cif", ".json")), "w") as f:
            json.dump(main_json_data, f, indent=4)

    def delete_structure_jsons(self, settings : AppSettings):
        json_dir = settings.json_drop_folder_path
        pr_cif_name = os.path.basename(self.primary_cif)
        pr_jsons_paths : list[str] = [os.path.join(json_dir, pr_cif_name.replace(".cif", "_trans.json")),
                                        os.path.join(json_dir, pr_cif_name.replace(".cif", "_axes.json"))]
        for path in pr_jsons_paths: 
            if os.path.exists(path): os.remove(path)

        for atom in self.atoms_cifs:
            name = os.path.basename(atom)
            json_path = os.path.join(json_dir, name.replace(".cif", "_trans.json"))
            if os.path.exists(json_path): os.remove(json_path)
            json_path = os.path.join(json_dir, name.replace(".cif", "_axes.json"))
            if os.path.exists(json_path): os.remove(json_path)
        
# FILE PROCESSING FUNCTIONS ####################################################

def read_from_cif(path):
    a, b, c, beta, gamma = (0, 0, 0, 0, 0)
    setup = 0

    try:
        with open(path, "r") as f:
            lines = f.readlines()
            for line in lines:
                splitted = line.replace("\n","").split()
                if len(splitted) <= 1: continue

                if "_cell_length_a" in splitted[0]: a = float(splitted[1].split("(")[0])
                if "_cell_length_b" in splitted[0]: b = float(splitted[1].split("(")[0])
                if "_cell_length_c" in splitted[0]: c = float(splitted[1].split("(")[0])

                # Define the setup of monoclinic cell 
                if "_cell_angle_beta" in splitted[0]:
                    beta = splitted[1].split("(")[0]
                    if beta == "90": setup = SETUP_GAMMA
                    beta = float(beta)
                if "_cell_angle_gamma" in splitted[0]:
                    gamma = splitted[1].split("(")[0]
                    if gamma == "90": setup = SETUP_BETA
                    gamma = float(gamma)

                if beta != 0 and gamma != 0: break
        
        if beta > 0 and gamma > 0:
            return MonoclinicCrystal(a, b, c, beta, gamma, path, setup)
        else:
            return None
    except:
        return None


def obtain_cif_files(directory):
    file_list : list[str] = []
    for root, dirs, files in os.walk(directory):
        if root != directory: continue
        file_list = files
    file_list.sort()
    return file_list


def obtain_crystals_list_from_cif_files(cif_folder_dir: str, file_list: list[str]):
    """
    Obtain list of structures from sorted list of cif-files
    """
    structures_list : list[MonoclinicCrystal] = []
    current_structure : MonoclinicCrystal = None

    skip_ref = "123"
    for file in file_list:
        if file.startswith(skip_ref): continue

        path = os.path.join(cif_folder_dir, file)
        if current_structure is None: 
            current_structure = read_from_cif(path)

            if current_structure is None: 
                skip_ref = file[:6]
                continue
            else:
                skip_ref = "123"
        elif file[:6] == current_structure.refcode:
            current_structure.atoms_cifs.append(path)
        else:
            structures_list.append(copy.deepcopy(current_structure))
            current_structure = read_from_cif(path)

            if current_structure is None: 
                skip_ref = file[:6]
                continue
            else:
                skip_ref = "123"
    return structures_list

# CALCULATION PROCESSING #######################################################

def assemble_args(cif_path: str, ops_block : OperatorBlock, only_calc: bool, settings: AppSettings) -> list[str]:
    args = [settings.apexcore_path]
    ops = ops_block

    # If the calculation is carried out for the found translations, then the APEXSYMM is launched with --norefine
    if only_calc: args.append(ops.u_trans_affine + ";" + ops.v_trans_affine)
    else: args.append(ops.axes_and_planes[:-1])

    args.append(cif_path)

    # Path to drop .jsons-files
    cif_name = os.path.basename(cif_path)
    if settings.json_drop_folder_path != "":
        mode_prefix = ""
        if only_calc: mode_prefix = "trans"
        else: mode_prefix = "axes"
        args.append("--json")
        args.append(os.path.join(settings.json_drop_folder_path, cif_name.replace(".cif",f"_{mode_prefix}.json")))

    if only_calc: args.append("--norefine")
    return args


def extract_etas_from_stdout(stdout: str):
    etas = []
    splitted = stdout.split("\n")

    for i in range(0, len(splitted)):
        if "OUTPUT_ETA" in splitted[i]:
            val = float(splitted[i+1].replace("\n", "").replace(" ",""))
            etas.append(val)

    return tuple(etas)    


def calc_ps_by_apexsymm(args):
    if args is None: return None
    result = sb.run(args, capture_output=True, text=True)
    etas = extract_etas_from_stdout(result.stdout)
    return etas


def is_meets_n_tot_criteria(structure : MonoclinicCrystal, op_block : OperatorBlock, settings : AppSettings):
    # Translations pseudosymmetry is checked at first
    args = assemble_args(structure.primary_cif, op_block, True, settings)
    etas = calc_ps_by_apexsymm(args)

    if etas is None or len(etas) != 2: return False
    # There's only 2 translations calculated in no-refine mode
    if etas[0] < settings.ntot_threshold or etas[1] < settings.ntot_threshold: return False
    
    # If it's good then axes and planes pseudosymmetry is checked
    args = assemble_args(structure.primary_cif, op_block, False, settings)
    etas = calc_ps_by_apexsymm(args)

    if etas is None or len(etas) == 0: return False
    if max(etas) < settings.ntot_threshold: return False
    return True


def is_meets_n_subl_min_criteria(structure : MonoclinicCrystal, op_block : OperatorBlock, settings : AppSettings):
    structure.current_n_subl_max_arr = []

    for atom_cif in structure.atoms_cifs:
        max_etas_for_atoms : list[float] = []
        # Translations pseudosymmetry is checked at first
        args = assemble_args(atom_cif, op_block, True, settings)
        etas = calc_ps_by_apexsymm(args)

        if etas is None or len(etas) != 2: return False
        # There's only 2 translations calculated in no-refine mode
        if etas[0] < settings.nsmin_threshold or etas[1] < settings.nsmin_threshold: return False
        max_etas_for_atoms.append((etas[0], etas[1]))

        # If it's good then axes and planes pseudosymmetry is checked
        args = assemble_args(atom_cif, op_block, False, settings)
        etas = calc_ps_by_apexsymm(args)

        if etas is None or len(etas) == 0: return False
        if max(etas) < settings.nsmin_threshold: return False
        max_etas_for_atoms.append(max(etas))

    structure.current_n_subl_max_arr.append(max_etas_for_atoms)
    return True


def is_meets_n_subl_max_criteria(structure : MonoclinicCrystal, settings : AppSettings):
    found_meets_n_subl_max_criteria = False
    
    for atom_etas in structure.current_n_subl_max_arr:
        if found_meets_n_subl_max_criteria: break

        if atom_etas[0][0] < settings.nsmax_threshold or atom_etas[0][1] < settings.nsmax_threshold: continue
        if atom_etas[1] < settings.nsmax_threshold: continue

        found_meets_n_subl_max_criteria = True

    return found_meets_n_subl_max_criteria

# MAIN #########################################################################

def main():
    settings = AppSettings.parse_cli()
    if not settings.is_valid(): exit(100)

    print(f"Collectioning all structures from {settings.cif_folder_path} dir...")
    file_list = obtain_cif_files(settings.cif_folder_path)
    structure_list = obtain_crystals_list_from_cif_files(settings.cif_folder_path, file_list)

    print("Calculations begins!")
    print("It seems to take a lot of time. Be patient a little... :)")

    # For progress count
    processed = 0
    max_process = len(structure_list)

    # Main loop for all structures processing
    for struct in structure_list:
        processed += 1
        suitable_struct = False
        approved_mnpq : list[ApprovedDescriptor] = []
        op_blocks_check : list[OperatorBlock] = []

        print(f">> {struct.refcode} NOW IN PROGRESS ({int(processed/max_process*100)}% is done)")

        struct.create_cart_matrix()
        approved_mnpq = struct.get_suitable_mnpq(settings)
        op_blocks_check = struct.get_operator_to_check_blocks(approved_mnpq, settings)

        for op_block in op_blocks_check:
            if not is_meets_n_tot_criteria(struct, op_block, settings): 
                struct.delete_structure_jsons(settings)
                continue
            if not is_meets_n_subl_min_criteria(struct, op_block, settings): 
                struct.delete_structure_jsons(settings)
                continue
            if not is_meets_n_subl_max_criteria(struct, settings): 
                struct.delete_structure_jsons(settings)
                continue
            suitable_struct = True
            # Хватит и одного блока, остальные можно найти потом. 
            # Это будет загруз лишний
            break
        
        if suitable_struct:
            print(f"\033[1;;42m>> {struct.refcode} IS GOOD\033[0m! Please check it later c:")
            struct.unite_structure_jsons_to_one(settings)
            struct.save_primary_cif(settings)
            
        struct.delete_structure_jsons(settings)
        struct.delete_structure_cifs()
    
    print("ALL IS DONE!")


main()