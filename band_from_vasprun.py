#!/usr/bin/env python3
# coding: utf-8

## TODO - log this function

import sys, argparse, logging
import pandas as pd

from pymatgen.electronic_structure.plotter import BSPlotter
from pymatgen.io.vasp import BSVasprun

# Adopted format: level - current function name - mess. Width is fixed as visual aid
c_log = logging.getLogger(__name__)
std_format = '[%(levelname)5s - %(funcName)10s] %(message)s'
logging.basicConfig(format=std_format)
c_log.setLevel(logging.WARNING)

def band_from_vasprun(vasprun: BSVasprun) -> int:
    """
    Useful docstring. This is called from argparse so make it clear;
    i.e multiples 3 numbers and returns thew output
    """
    bandstructure = vasprun.get_band_structure()
    b = BSPlotter(bs=bandstructure)
    return x  # Try to return the pymatgen format here so it can still be used as a function


def cli_run(argv) -> None:
    """
    Wrapper for the above command, handles parsing of args and logging, to avoid mess
    """

    global c_log

    parser = argparse.ArgumentParser(description=band_from_vasprun.__doc__)  # Parser init
    parser.add_argument("vasprun", type=str, default="vasprun.xml", help="vasprun file location")
    parser.add_argument("--optional", dest="optional", type=int, default=4, help="OptionalArgument")
    parser.add_argument("--debug", dest="debug", action="store_true")  # Always have the debug optional
    parser.add_argument("--verbose", dest="verbose", action="store_true")  # Always have the verbose optional

    args = parser.parse_args(argv)

    if args.debug:  # Always include method for switching verbosity
        c_log.setLevel(logging.DEBUG)
    if args.verbose:
        c_log.setLevel(logging.INFO)
    c_log.debug(args)

    vasprun = BSVasprun(filename=args.vasprun)


if __name__ == "__main__":
    cli_run(sys.argv[1:])