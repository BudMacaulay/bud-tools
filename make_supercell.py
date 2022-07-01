#!/usr/bin/env python3
# coding: utf-8

import sys, argparse, logging
from typing import Optional, List

from pymatgen.core import Structure
from pymatgen.io.vasp import Poscar

# Adopted format: level - current function name - mess. Width is fixed as visual aid
c_log = logging.getLogger(__name__)
std_format = '[%(levelname)5s - %(funcName)10s] %(message)s'
logging.basicConfig(format=std_format)
c_log.setLevel(logging.WARNING)


def make_supercell(structure: Structure, scale_matrix: Optional[List[int]] = None) -> Structure:
    """
    Uses pymatgen structure to make a supercell very simple.
    """

    if scale_matrix is None:  # Init if not supplied
        scale_matrix = [1, 1, 1]
    if scale_matrix == [1, 1, 1]:
        c_log.warning(f"Scale Matrix not supplied, scaling by 1,1,1 [i.e dumping back poscar]")

    c_log.info(f"Structure Info {structure}")
    c_log.info(f"Scaled by {scale_matrix}")

    structure.make_supercell(scaling_matrix=scale_matrix)
    c_log.info(f"Supercell Size: {len(structure)}")
    return structure


def cli_run(argv) -> None:
    """
    Wrapper for the above command, handles parsing of args and logging, to avoid mess
    """

    global c_log

    parser = argparse.ArgumentParser(description=make_supercell.__doc__)  # Parser init
    parser.add_argument("poscar", type=str, default="POSCAR", help="Location of POSCAR file", nargs="?")
    parser.add_argument("scale_matrix", type=int, nargs=3, default=[1, 1, 1],
                        help="Scaling matrix as space separated integers")

    parser.add_argument("--verbose", dest="verbose", action="store_true", help="verbose printing")
    parser.add_argument("--debug", dest="debug", action="store_true", help="flag for debugging")  # Always debug
    args = parser.parse_args(argv)

    if args.debug:
        c_log.setLevel(logging.DEBUG)
    if args.verbose:
        c_log.setLevel(logging.INFO)
    c_log.debug(args)

    structure = Structure.from_file(filename=args.poscar)
    print(Poscar(make_supercell(structure=structure, scale_matrix=args.scale_matrix)))


if __name__ == "__main__":
    cli_run(sys.argv[1:])
