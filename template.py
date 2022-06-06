#!/usr/bin/env python3
# coding: utf-8

import sys, argparse, logging

# Adopted format: level - current function name - mess. Width is fixed as visual aid
c_log = logging.getLogger(__name__)
std_format = '[%(levelname)5s - %(funcName)10s] %(message)s'
logging.basicConfig(format=std_format)
c_log.setLevel(logging.WARNING)


def called_function(var_1: int = 1, var_2: int = 2, var_3: int = 3) -> int:
    """
    Useful docstring. This is called from argparse so make it clear;
    i.e multiples 3 numbers and returns thew output
    """

    c_log.debug(f"var1:{var_1}, var2:{var_2}, var3:{var_3}3 ")
    x = var_1 * var_2 * var_3
    return x  # Try to return the pymatgen format here so it can still be used as a function


def cli_run(argv) -> str:
    """ Wrapper for the above command, handles parsing of args and logging, to avoid mess """
    global c_log

    parser = argparse.ArgumentParser(description=called_function.__doc__)  # Parser init
    parser.add_argument("positional_argument", type=str, default="NONE", help="PositionalArgument")
    parser.add_argument("--optional", dest="optional", type=int, default=4, help="OptionalArgument")
    parser.add_argument("--debug", dest="debug", action="store_true") # Always have the debug optional
    parser.add_argument("--verbose", dest="verbose", action="store_true")  # Always have the verbose optional

    args = parser.parse_args(argv)

    if args.debug:  # Always include method for switching verbosity
        c_log.setLevel(logging.DEBUG)
    if args.verbose:
        c_log.setLevel(logging.INFO)

    print(called_function(var_1=1, var_2=2, var_3=3))  # Writting to the CLI happens in cli run to seperate pmg from cli


if __name__ == "__main__":
    cli_run(sys.argv[1:])