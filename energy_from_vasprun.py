#!/usr/bin/env python3
# coding: utf-8

import sys, argparse, logging
import pandas as pd
from numpy import linalg as la

from pymatgen.io.vasp import Vasprun

# Adopted format: level - current function name - mess. Width is fixed as visual aid
c_log = logging.getLogger(__name__)
std_format = '[%(levelname)5s - %(funcName)10s] %(message)s'
logging.basicConfig(format=std_format)
c_log.setLevel(logging.WARNING)

def energy_from_vasprun(vs: Vasprun, resolution: int = 1, electronic: bool = False) -> str:
    """
    Gets Energies from vasprun and returns the change in force as convergence improves
    """

    x = ["ION_STEP"]
    y = ["Energy"]
    x_2 = ["E_STEP"]
    for step, result in enumerate(vs.ionic_steps[::resolution]):
        if electronic:
            for num, elec in enumerate(result["electronic_steps"]):
                x_2.append(num)
                y.append(round(elec["e_fr_energy"], 5))
                x.append(step * resolution)
        else:
            energy = result["e_fr_energy"]
            y.append(round(energy, 5))

    if electronic:
        zp = zip(x, x_2, y)
    else:
        zp = zip(x, y)
    p = pd.DataFrame(zp)
    return p.to_string(header=False, index=False)


def cli_run(argv) -> None:
    """
    Wrapper for the above command, handles parsing of args and logging, to avoid mess
    """

    global c_log

    parser = argparse.ArgumentParser(description=energy_from_vasprun.__doc__)  # Parser init
    parser.add_argument("vasprun", type=str, default="vasprun.xml", help="vasprun file location")

    parser.add_argument("-r", "--res", dest="resolution", default=1, type=int,
                        help="Parse vasprun for every nth ionic step")
    parser.add_argument("-e", "--electronic", action="store_true",
                        help="whether to parse energies per every electronic step")
    parser.add_argument("--debug", dest="debug", action="store_true")  # Always have the debug optional
    parser.add_argument("--verbose", dest="verbose", action="store_true")  # Always have the verbose optional

    args = parser.parse_args(argv)

    if args.debug:  # Always include method for switching verbosity
        c_log.setLevel(logging.DEBUG)
    if args.verbose:
        c_log.setLevel(logging.INFO)

    vs = Vasprun(filename=args.vasprun,
                 ionic_step_skip=0, ionic_step_offset=0,
                 parse_dos=False, parse_eigen=False,
                 parse_projected_eigen=False, parse_potcar_file=False, occu_tol=1e-8, exception_on_bad_xml=True)

    print(energy_from_vasprun(vs=vs, resolution=args.resolution))

if __name__ == "__main__":
    cli_run(sys.argv[1:])
