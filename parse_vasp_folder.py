#!/usr/bin/env python3
# coding: utf-8

import sys, argparse, logging


from pymatgen.io.vasp import Oszicar
from pymatgen.io.vasp import Vasprun
from pymatgen.io.vasp import Outcar
from pymatgen.core import Structure

# Adopted format: level - current function name - mess. Width is fixed as visual aid
c_log = logging.getLogger(__name__)
std_format = '[%(levelname)5s - %(funcName)10s] %(message)s'
logging.basicConfig(format=std_format)
c_log.setLevel(logging.WARNING)


def parse_vasp_folder() -> None:
    """
    Method for parsing a folder containing a vasp calculation and parsing potentially important information.
    """
    pass

def cli_run(argv) -> None:
    """
    Wrapper for the above command, handles parsing of args and logging, to avoid mess
    """

    global c_log

    parser = argparse.ArgumentParser(description=called_function.__doc__)  # Parser init
    parser.add_argument("positional_argument", type=str, default="NONE", help="PositionalArgument")
    parser.add_argument("--optional", dest="optional", type=int, default=4, help="OptionalArgument")
    parser.add_argument("--debug", dest="debug", action="store_true")  # Always have the debug optional
    parser.add_argument("--verbose", dest="verbose", action="store_true")  # Always have the verbose optional

    args = parser.parse_args(argv)

    if args.debug:  # Always include method for switching verbosity
        c_log.setLevel(logging.DEBUG)
    if args.verbose:
        c_log.setLevel(logging.INFO)

    print(called_function(var_1=1, var_2=2, var_3=3))  # Writing to the CLI happens in cli run to separate pmg from cli


if __name__ == "__main__":
    cli_run(sys.argv[1:])
