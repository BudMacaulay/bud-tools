#!/usr/bin/env python3
# coding: utf-8

import sys, argparse, logging

# Adopted format: level - current function name - mess. Width is fixed as visual aid
c_log = logging.getLogger(__name__)
std_format = '[%(levelname)5s - %(funcName)10s] %(message)s'
logging.basicConfig(format=std_format)
c_log.setLevel(logging.WARNING)


def spincar_from_chgcar(chgcar_file: str = "CHGCAR") -> Structure:
    """
    Very simple routine to split the chgcar into a spin density only file. Used in visualisation of spin densities
    """
    global c_log
    lines = []
    with open(chgcar_file) as f:
        for i in f.readlines():
            lines.append(i)
    
    c_log.debug(f"Total Line count for chgcar file {len(lines)}")
    search_pattern = lines[lines.index(' \n') + 1]
    c_log.debug(f"Searching lines for search pattern: '{search_pattern}'")
    app = [i for i, x in enumerate(lines) if x==search_pattern]
    c_log.debug(f"Total: {len(app)}, Expected: 2")

    if len(app) > 2:
        c_log.warning('weird, you have too many of the search pattern. Unsure what to do, talk to Bud prhaps')
        return
    spincar = lines[1:app[0]] + lines[app[1]:]
    spincar_st = "\n".join(spincar)
    return "\n".join(spincar)


def cli_run(argv) -> str:
    """ Wrapper for the above command, this is basically a quitck and easy wrap for pymatgen stuff """
    global c_log

    parser = argparse.ArgumentParser(description=spincar_from_chgcar.__doc__)  # Parser init
    parser.add_argument("chgcar", type=str, default="CHGCAR", help="location of CHGCAR file")
    parser.add_argument("--debug", dest="debug", action="store_true")
    args = parser.parse_args(argv)

    if args.debug:   # Verbose setting
        c_log.setLevel(logging.DEBUG)

    print(spincar_from_chgcar(args.chgcar))


if __name__ == "__main__":
    cli_run(sys.argv[1:])
