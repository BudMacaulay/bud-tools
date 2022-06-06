#!/usr/bin/env python3
# coding: utf-8

import sys, argparse, logging
from pymatgen.core import Structure
from pymatgen.io.vasp import Poscar

# Adopted format: level - current function name - mess. Width is fixed as visual aid
c_log = logging.getLogger(__name__)
std_format = '[%(levelname)5s - %(funcName)10s] %(message)s'
logging.basicConfig(format=std_format)
c_log.setLevel(logging.WARNING)


def scale_abc(structure: Structure, volume_change: float) -> Structure:
    """
    Uses pymatgen structure to scale lattice dimensions to new volume
    """

    volume = structure.volume * (1 + volume_change)
    c_log.info(f"new volume shall be {round(volume, 3)}")
    c_log.info(f"Structure Info: {len(structure)}")
    c_log.info(f"Original Volume: {round(structure.volume,0)}")
    structure.scale_lattice(volume=volume)
    return structure


def cli_run(argv) -> str:
    """
    Wrapper for the above command, handles parsing of args and logging, to avoid mess
    """
    global c_log

    parser = argparse.ArgumentParser(description=scale_abc.__doc__)  # Parser init
    parser.add_argument("poscar", type=str, default="POSCAR", help="Location of POSCAR file", nargs="?")
    parser.add_argument("vol_chn", type=float, nargs="?",
                        help="volume change as a fraction")

    parser.add_argument("--verbose", dest="verbose", action="store_true", help="verbose printing")
    parser.add_argument("--debug", dest="debug", action="store_true", help="Debugflag") # Always have the debug optional
    args = parser.parse_args(argv)

    if args.debug:  # Always include method for switching verbosity
        c_log.setLevel(logging.DEBUG)
    if args.verbose:
        c_log.setLevel(logging.INFO)
    c_log.debug(args)

    structure = Structure.from_file(filename=args.poscar)
    print(Poscar(scale_abc(structure=structure, volume_change=args.vol_chn)))


if __name__ == "__main__":
    cli_run(sys.argv[1:])
