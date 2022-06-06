#!/usr/bin/env python3

import argparse, logging, os, sys

import numpy as np
from pymatgen.core.surface import SlabGenerator
from pymatgen.core.surface import Structure, get_symmetrically_equivalent_miller_indices
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

c_log = logging.getLogger(__name__)
# Adopted format: level - current function name - mess. Width is fixed as visual aid
std_format = '[%(levelname)5s - %(funcName)10s] %(message)s'
logging.basicConfig(format=std_format)
c_log.setLevel(logging.WARNING)


def make_surface(init_structure: Structure, miller_index: tuple = None,
                 layer_size: int = 7, vac_size: int = 13,
                 mode: str = "move-sites") -> None:

    global c_log
    # Guess the oxidation states to detect dipole
    init_structure.add_oxidation_state_by_guess()

    if miller_index is None:
        c_log.warning("NO Miller index supplied defaulting to 0 0 1")
        miller_index = [0, 0, 1]

    if not all((type(x) == int for x in miller_index)):  # ERROR HANDLE
        c_log.warning("Non-integer values in miller index - im not sure how pymatgen handles this so crashing")
        return

    sg = SpacegroupAnalyzer(init_structure)
    c_log.debug("Initialising guess Oxidation States")
    spec = [x for x in set(init_structure.species)]
    c_log.info(f"Ox states are as: {' '.join(str(x) for x in spec)}")
    c_log.info(f"Desired miller Index is: {miller_index}")
    c_log.info(
        f"Space Group is {sg.get_space_group_number()}, {sg.get_space_group_symbol()} {sg.get_crystal_system()}\n")

    conv = sg.get_conventional_standard_structure()
    if not conv == init_structure:
        c_log.warning(f"Input structure is not in standard format for this space group")
        c_log.warning(
            f"proceeding to cut the slab using the miller plane from the current lattice - This may be undesired\n")

    c_log.info(f"Within current structure: Symmetry equivalent indices to {miller_index}:\n"
               f""
               f"{get_symmetrically_equivalent_miller_indices(structure=init_structure, miller_index=miller_index)[1:]}"
               f"\n")

    t = SlabGenerator(initial_structure=init_structure, miller_index=miller_index, in_unit_planes=False,
                      reorient_lattice=True, min_slab_size=layer_size, min_vacuum_size=vac_size,
                      lll_reduce=True, center_slab=True, max_normal_search=max(miller_index))

    if mode == "break-stio":
        slabs = t.get_slabs(symmetrize=True, repair=True)
    elif mode == "move-sites":
        slabs = t.get_slabs(symmetrize=False, repair=True)
    else:
        c_log.warning(f"mode: {mode} not found, Exiting")
        return

    datafile = [["NAME", "SIZE", "Area", "Cnorm", "Symmetry", "Polarity", "Tasker Type"]]
    work_on = []
    c_log.info(f"Total number of initial slabs: {len(slabs)}")
    for n, slab in enumerate(slabs):
        slab.sort()
        if not slab.is_polar() and slab.is_symmetric():
            c_log.debug(f"Slab {n}: is Tasker Type 2")
            fn = f"slabs/type2_{n}_{''.join(str(a) for a in slab.miller_index)}.vasp"
            slab.to(fmt="poscar", filename=fn)
        else:
            c_log.debug(f"Slab {n}: is Tasker Type 3; saving and also adding to reconstruction list")
            fn = f"slabs/type3_{n}_{''.join(str(a) for a in slab.miller_index)}.vasp"
            slab.to(fmt="poscar", filename=fn)
            sc = slab
            sc.make_supercell(scaling_matrix=[2, 1, 1])
            work_on.extend(sc.get_tasker2_slabs())
        datafile.append(
            [fn.split("/")[-1], len(slab), round(slab.surface_area, 3), round(slab.normal[2], 3), slab.is_symmetric(),
             np.linalg.norm(slab.dipole / slab.surface_area)])

    c_log.info(f"Total number of Tasker type 3 slabs: {len(work_on)}")
    c_log.info(f"Proceeding to tasker 2 said slabs")
    for n, slab in enumerate(work_on):
        slab.sort()
        if not slab.is_polar(tol_dipole_per_unit_area=1e-2) and slab.is_symmetric():
            fn = f"slabs/tc_type2_{len(slabs) + n}_{''.join(str(a) for a in slab.miller_index)}.vasp"
            slab.to(fmt="poscar", filename=fn)
        else:
            fn = f"slabs/failedtc_type3_{len(slabs) + n}_{''.join(str(a) for a in slab.miller_index)}.vasp"
            slab.to(fmt="poscar", filename=fn)
        datafile.append(
            [fn.split("/")[-1], len(slab), round(slab.surface_area), round(slab.normal[2], 3), slab.is_symmetric(),
             np.linalg.norm(slab.dipole / slab.surface_area)])

    with open("slabs/make_surface.dat", "w+") as f_ile:
        for line in datafile:
            f_ile.writelines(" ".join(str(x) for x in line))

    return


def cli_run(argv) -> None:
    """
    Wrapper for the above command, this is basically a quick and easy wrap for pymatgen stuff
    """

    global c_log

    parser = argparse.ArgumentParser(description=make_surface.__doc__)
    # Someone make argparse a little easier to read the docs before i scream #
    parser.add_argument("bulk_poscar", type=str, help="BULK POSCAR YOU WISH TO SLICE")
    parser.add_argument("-m", dest="millerplane", help="The miller plane you would like to slice across", nargs=3,
                        type=int)

    # Optional flags - these probably need some fiddling and are likely system dependant
    parser.add_argument("-v", dest="vac", default=20, help="vacuum size", type=float)
    parser.add_argument("-l", dest="lay", default=11, type=float,
                        help="layers to generate (in angstrom - Good values are 11+")
    parser.add_argument("--mode", dest="recon_mode", default="move-sites", type=str,
                        help="Mode to fix Tasker type 3 slabs, either move-sites (default) or break-stio.")

    parser.add_argument("--verbose", dest="verbose", action="store_true")
    parser.add_argument("--debug", dest="debug", action="store_true")
    args = parser.parse_args(argv)

    if args.verbose:
        c_log.setLevel(logging.INFO)
    elif args.debug:
        c_log.setLevel(logging.DEBUG)

    c_log.debug(args)

    os.makedirs("slabs/", exist_ok=True)
    init_structure = Structure.from_file(args.bulk_poscar)
    make_surface(init_structure, miller_index=args.millerplane, vac_size=args.vac, layer_size=args.lay,
                 mode=args.recon_mode)


if __name__ == "__main__":
    cli_run(sys.argv[1:])
