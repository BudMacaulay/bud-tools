#!/usr/bin/env python3
# coding: utf-8

import sys, argparse, logging
from itertools import product
import time

from pymatgen.core import Structure
from pymatgen.analysis import ewald

# Adopted format: level - current function name - mess. Width is fixed as visual aid
c_log = logging.getLogger(__name__)
std_format = '[%(levelname)5s - %(funcName)10s] %(message)s'
logging.basicConfig(format=std_format)
c_log.setLevel(logging.WARNING)


def get_ox_poscar(filename: str):
    ll = []
    with open(filename) as file:
        for line in file:
            ll.append(line)

    ion_line = ll[6].split()
    scrape = 0
    for i in ion_line:
        try:
            scrape += int(i)
        except ValueError:
            c_log.info(f"Found non integer value on ion_line, skipping: {i}")
            pass

    count = 8
    if ll[7].lower().startswith("s"):
        c_log.info(f"Selective dynamics line found in POSCAR, adding 1 to the line scraper")
        count += 1

    # Assume all following lines are T T Ts Atomics or Pot ox states and thus attempt to parse only floats.
    ox_states = []
    for line in ll[count:count + scrape]:
        aft_coord = line.split()[3:]
        a = []
        for i in aft_coord:
            try:
                a.append(float(i))
            except ValueError:
                pass
        ox_states.append(a)
    return ox_states


def ewald_opt_from_ox(structure: Structure, ox_states_matrices, check_charge=True) -> list:
    """
    What was expected to just be a wrapped of a piece of pymatgen code
    instead has become me painstaking reading 2 wiki pages on Ewald Calculations aswell as 2000 lines of f90
    from the dark ages of programming

    Pymatgen does have a piece of ewald opt code, but thats only for defects and fractional substitutions
    [EwaldMinimizer]

    There maybe a equivalent conversion between variable oxidation states and effective reduction in composition but
    that seemed too hard
    Input: structure (Pymatgen Structure)
    ox_state_matrices in form [[1,0], [2,0] [2,1] [3,2] [0,1]]
    check_charge: bool, whether to ensure charge is not charged.
    If its supplied in a different form the code will (try?!) to clean it up.

    This method invokes the same structure across all calculations which speeds up subsequent calls to the ewald
    sum call

    TODO - If initial state has a species with Ox = 0 then the pymatgen call will crash.
     Not sure if this is a realistic approach or not.

    TODO - Implement the monte carlo method that is on pymatgen for defect ewald summation since large cells + multiple ox states
     results in a mess


    """

    # Consistancy checks:
    if len(ox_states_matrices) != len(structure):
        c_log.warning(f"length of ox_matrix and structure are non-equivalent... Skipping for now")
        return

    perm_cost = 1
    for i in ox_states_matrices:
        perm_cost *= len(i)

    if perm_cost > 2E06:
        c_log.warning(f"Huge amount of possible permutations from ox_states: {perm_cost}, exitting as generation"
                      f" of perms will crash")
        return

    permutation_list = list(product(*ox_states_matrices))

    c_log.info(f"Total Permuatations: {len(permutation_list)}")
    if check_charge:
        c_log.info(f"Stripping charged final structures (if sum(perrm) == 0 )")
        permutation_list = [x for x in permutation_list if sum(x) == 0]

    cost = len(structure) * len(permutation_list)
    if len(cost) > 2000:
        c_log.warning(f"total permutations to ewald sum is > 1000, this may hang. For now proceeding")
    if len(permutation_list) > 1E06:
        c_log.warning(f"okay, permutation cost is > 1E6, Exitting to save your PC. Expected to take afew minutes")
        c_log.warning(f"If someone wants to come up with a Monte Carlo methos that iterates smartly, go for it")
        return

    pm = permutation_list[0]
    structure.add_oxidation_state_by_site(oxidation_states=pm)
    ewa = ewald.EwaldSummation(structure)
    e_pm = [(sum(sum(ewa.total_energy_matrix)), pm)]

    t = time.time()
    for n, ox_states in enumerate(permutation_list[1:]):
        c_log.debug(f"Current on: {n} / {len(permutation_list[1:])}")
        s = structure.copy()
        s.add_oxidation_state_by_site(oxidation_states=ox_states)
        p = ewa.compute_sub_structure(sub_structure=s)  # Returns the sum(sum(total_energy_matrix)) Using a scale factor
        e_pm.append((p, ox_states))
        c_log.debug(f"Runtime: {round(time.time() - t, 3)}")
    e_pm.sort(key=lambda x: x[0])
    return e_pm


def cli_run(argv) -> None:
    """
    Wrapper for the above command, handles parsing of args and logging, to avoid mess
    """

    global c_log

    parser = argparse.ArgumentParser(description=ewald_opt_from_ox.__doc__)  # Parser init
    parser.add_argument("POSCAR", type=str, default="tests/POSCAR_Large.vasp", help="Location of a formatted POSCAR")
    parser.add_argument("c", "--check_charge", default=True, action="store_true", help="Whether to check for chg bal")
    parser.add_argument("--debug", dest="debug", action="store_true")  # Always have the debug optional
    parser.add_argument("--verbose", dest="verbose", action="store_true")  # Always have the verbose optional

    args = parser.parse_args(argv)

    if args.debug:  # Always include method for switching verbosity
        c_log.setLevel(logging.DEBUG)
    if args.verbose:
        c_log.setLevel(logging.INFO)
    c_log.debug(args)

    structure = Structure.from_file(filename=args.POSCAR)

    ox_states = get_ox_poscar(filename=args.POSCAR)
    x = ewald_opt_from_ox(structure=structure, ox_states_matrices=ox_states, check_charge=True)


if __name__ == "__main__":
    cli_run(sys.argv[1:])
