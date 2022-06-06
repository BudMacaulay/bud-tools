#!/usr/bin/env python3
# coding: utf-8

import sys, argparse, logging
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer


# Adopted format: level - current function name - mess. Width is fixed as visual aid
c_log = logging.getLogger(__name__)
std_format = '[%(levelname)5s - %(funcName)10s] %(message)s'
logging.basicConfig(format=std_format)
c_log.setLevel(logging.WARNING)


def symm_info(structure: Structure) -> SpacegroupAnalyzer:
    """
    Returns the symmetry info for a inputted structure.
    Based on kramergroup/symminfo an old f90 chunk.
    """

    sg = SpacegroupAnalyzer(structure)

    sg.get_symmetry_operations()
    return sg
    pass





def cli_run(argv) -> str:
    """ Wrapper for the above command, handles parsing of args and logging, to avoid mess """
    global c_log

    parser = argparse.ArgumentParser(description=symm_info.__doc__)  # Parser init
    parser.add_argument("POSCAR", type=str, default="POSCAR", help="location of poscar file")
    parser.add_argument("-p", dest="prim_cell", action="store_true",
                        help="Whether to dump the matrix transformation to primitive cell")
    parser.add_argument("-c", dest="conv_cell", action="store_true",
                        help="Whether to dump the matrix transformation to conventional cell")

    parser.add_argument("--debug", dest="debug", action="store_true") # Always have the debug optional
    parser.add_argument("--verbose", dest="verbose", action="store_true")  # Always have the verbose optional

    args = parser.parse_args(argv)

    if args.debug:  # Always include method for switching verbosity
        c_log.setLevel(logging.DEBUG)
    if args.verbose:
        c_log.setLevel(logging.INFO)

      # Writting to the CLI happens in cli run to seperate pmg from cli


if __name__ == "__main__":
    cli_run(sys.argv[1:])

