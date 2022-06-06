#!/usr/bin/env python3

import sys
import os, argparse, logging

from pymatgen.core import Structure, Lattice
from pymatgen.io.vasp import Poscar

# Init global logger for this scope.
c_log = logging.getLogger(__name__)
logging.basicConfig(format='[%(levelname)5s - %(funcName)10s] %(message)s')
c_log.setLevel(logging.WARNING)  # Initialise logging level to warning, this will only print out on well, warnings


def stretch_cell(structure: Structure, dimension: int = 2,
                 scale_amount: float = 0.05, fix_bonds: list = None) -> Structure:
    """ Method to stretch an input structure across a specified dimension with the optional choice to fix a particular bond length
    Pymatgen does all the heavy lifting, although pymatgen is stupid so yeah
    """
    global c_log

    c_log.info(f"Loaded Structure has: {len(structure)} sites")
    c_log.info(f"Composition: {structure.composition.formula}")

    l = list(structure.lattice.parameters)
    l[dimension] = l[dimension] * (1.00 + scale_amount)
    c_log.info(f"Initial Lattice dimensions: {l}")
    c_log.info(f"Stretching dimension {dimension} by {1.00 + scale_amount} of original")
    c_log.info(f"New Lattice dimensions: {l}")
    ns = Structure(coords=structure.frac_coords, species=structure.species, lattice=Lattice.from_parameters(*l))

    # Handle the edge case first
    if fix_bonds is None:
        return ns

    # If bond lengths are to be fixed
    c_log.info(f"Attempting to fix the bond lengths for {fix_bonds[0] and fix_bonds[1]}")
    c_log.debug(f"Distance Matrix for initial structure:\n {structure.distance_matrix.round(2)}")
    idx_fix2 = [(n, x) for n, x in enumerate(structure) if x.specie.value == fix_bonds[1]]

    shift_list = []
    for idx, site in idx_fix2:  # Pair each speices in fix_bonds[1] with a species in fix_bonds[2]
        neigh = structure.get_neighbors(site=site, r=3.5)
        neigh = [x for x in neigh if x.specie.value == fix_bonds[0]]
        x_idx = min(neigh, key=lambda x: x.nn_distance)
        c_log.debug(f"Oxygen {site} nearest neighbour is {x_idx} with index {x_idx.index}")
        c_shift = site.coords[dimension] - x_idx.coords[dimension]  # Shift value
        c_log.debug(f"With a shift value of: {c_shift}")
        shift_list.append((idx, x_idx.index, c_shift))

    for idx_1, idx_2, shift in shift_list:
        c_log.debug(f"Original: {ns[idx_1].coords[dimension]}")
        c_log.debug(f"Neighbour: {ns[idx_2].coords[dimension]}")
        c_log.debug(f"Shift: {shift}")
        # Stupidly Niave approach, cause why would changing the coords result in changing the coordss
        # ns[idx_1].coords[dimension] = new_structure[idx_2].coords[dimension] + shift
        new_xyz = [ns[idx_1].coords[0], ns[idx_1].coords[1], ns.coords[dimension] + shift]
        c_log.debug(f"Final: {new_xyz[dimension]}")
        ns.replace(i=idx_1, species=ns[idx_1].species, coords=new_xyz, coords_are_cartesian=True)

    return ns


def cli_run(argv) -> str:
    """Wrapper and Handler of above calls"""

    global c_log

    parser = argparse.ArgumentParser(description=stretch_cell.__doc__, epilog="Buddy 22")
    # Positional Args
    parser.add_argument("filename", default="CONTCAR", type=str, nargs="?",
                        help="Input file to load as a pymatgen structure")
    parser.add_argument("dimension", default=2, type=int, nargs="?",
                        help="Dimension in which to scale across")
    parser.add_argument("scale_amount", default=0.05, type=float, nargs="?",
                        help="Fractional Scale amount, defaults to 0.05 (5%)")

    # Optional Args
    parser.add_argument("--fix", dest="fix", default=None, type=list, nargs=2,
                        help="Bonds in which to fix upon scaling (i.e stretch across the other bonds)")
    # Loud Args
    parser.add_argument("--verbose", action="store_true", dest="verbose",
                        help="Loud printouts")
    parser.add_argument("--debug", action="store_true", dest="debug",
                        help="show debugging information, mostly if the code goes grossly wrong")
    args = parser.parse_args(argv)

    if args.verbose:
        c_log.setLevel(level=logging.INFO)
    elif args.debug:
        c_log.setLevel(level=logging.DEBUG)

    c_log.debug(args)

    structure = Structure.from_file(filename=args.filename)
    ns = stretch_cell(structure, dimension=args.dimension, scale_amount=args.scale_amount, fix_bonds=args.fix)
    print(Poscar(ns))


if __name__ == "__main__":
    cli_run(sys.argv[1:])
