#!/usr/bin/env python3
# coding: utf-8

import sys, argparse, logging

# Adopted format: level - current function name - mess. Width is fixed as visual aid
c_log = logging.getLogger(__name__)
std_format = '[%(levelname)5s - %(funcName)10s] %(message)s'
logging.basicConfig(format=std_format)
c_log.setLevel(logging.WARNING)

def called_function(var_1=1, var_2=2, var_3=3):
    """
    Useful docstring. This is called from argparse so make it clear;
    i.e multiples 3 numbers and returns thew output
    """

    c_log.debug(f"var1:{var_1}, var2:{var_2}, var3:{var_3}3 ")
    x = var_1 * var_2 * var_3
    return x
def cli_run(argv):
    """ Wrapper for the above command, handles parsing of args and logging, to avoid mess """
    global c_log

    parser = argparse.ArgumentParser(description=called_function.__doc__)  # Parser init
    parser.add_argument("positional_argument", type=str, default="NONE", help="PositionalArgument")
    parser.add_argument("--optional", dest="optional", type=int, default=4, help="OptionalArgument")
    parser.add_argument("--debug", dest="debug", action="store_true") # Always have the debug optional

    args = parser.parse_args(argv)

    if args.debug:  # Always include method for switching verbosity
        c_log.setLevel(logging.DEBUG)
    if args.verbose:
        c_log.setLevel(logging.INFO)
    called_function(var1=1, var2=2, var_3=3) # Handling of printouts and file creation within the function.

if __name__ == "__main__":
    cli_run(sys.argv[1:])