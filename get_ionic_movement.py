#!/usr/bin/env python3
# coding: utf-8

# TODO Make the print out a little nicer.

import sys, argparse, logging
import numpy as np

from pymatgen.core import Structure

# Adopted format: level - current function name - mess. Width is fixed as visual aid
c_log = logging.getLogger(__name__)
std_format = '[%(levelname)5s - %(funcName)10s] %(message)s'
logging.basicConfig(format=std_format)
c_log.setLevel(logging.WARNING)


def get_ionic_delta(structure_1: Structure, structure_2: Structure) -> tuple:
    """
    Method to return the matrix of ionic movement between two structures.

    Must ensure that the atomic indexes line up completely. i/e Atom 1 is consistant
    """

    # diff = structure_1.cart_coords - structure_2.cart_coords (This method is poor in pbc)
    # instead use vvvv

    if structure_1.lattice != structure_2.lattice:
        c_log.warning(f"Care! Lattices are not equivalent, may result in some issues")

    dist = []
    for n, x in enumerate(structure_1):
        dist.append(x.distance_and_image(other=structure_2[n])[0])

    vec = []
    for n, x in enumerate(structure_1):
        vec.append(structure_2[n].coords - x.coords)

    dist = np.around(dist, decimals=4)
    vec = np.around(vec, decimals=4)
    return dist, vec


def cli_run(argv) -> None:
    """
    Wrapper for the above command, handles parsing of args and logging, to avoid mess
    """

    global c_log

    parser = argparse.ArgumentParser(description=get_ionic_delta.__doc__)  # Parser init

    parser.add_argument("file_1", type=str, default="POSCAR", nargs="?", help="PositionalArgument")
    parser.add_argument("file_2", type=str, default=4, nargs="?", help="OptionalArgument")

    parser.add_argument("-s", "--strip", dest="strip", action="store_true",
                        help="Whether top strip low displacement ions from the print out")
    parser.add_argument("--debug", dest="debug", action="store_true")  # Always have the debug optional
    parser.add_argument("--verbose", dest="verbose", action="store_true")  # Always have the verbose optional

    args = parser.parse_args(argv)

    if args.debug:  # Always include method for switching verbosity
        c_log.setLevel(logging.DEBUG)
    if args.verbose:
        c_log.setLevel(logging.INFO)
    c_log.debug(args)

    strip_val = 0
    if args.strip:
        strip_val = 0.05

    structure_1 = Structure.from_file(filename=args.file_1)
    structure_2 = Structure.from_file(filename=args.file_2)

    dist, vec = get_ionic_delta(structure_1, structure_2)

    disp_str = "Number        Distance        Vector\n" # Converting into nice print format
    for n, x in enumerate(dist): # Strip values for the strip flag
        if x > strip_val:
            disp_str += f"Atom {n}:        {round(x, 4)}        {vec[n]}\n"
    print(disp_str)


if __name__ == "__main__":
    cli_run(sys.argv[1:])
