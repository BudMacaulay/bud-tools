#!/usr/bin/env python3
# coding: utf-8

import sys, argparse, logging
import numpy as np
import re

from pymatgen.core import Structure
from pymatgen.io.vasp import Poscar
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

# Adopted format: level - current function name - mess. Width is fixed as visual aid
c_log = logging.getLogger(__name__)
std_format = '[%(levelname)5s - %(funcName)10s] %(message)s'
logging.basicConfig(format=std_format)
c_log.setLevel(logging.WARNING)


def symm_info(structure: Structure) -> SpacegroupAnalyzer:
    """
    Returns the symmetry info for a inputted structure.
    Based on kramergroup/symminfo an old f90 chunk. Since this method is basically the whole symopps package.

    It acts mostly as a string formatter
    """

    return SpacegroupAnalyzer(structure)


def operations_to_str(sg: SpacegroupAnalyzer) -> str:
    """
    Converts the symmetry operations into a Kramer desired output
    """

    sg_op = [len(sg.get_symmetry_operations())]
    fm = {'float_kind': lambda x: "%.6f" % x}
    for op in sg.get_symmetry_operations():
        rm = op.rotation_matrix
        tv = op.translation_vector
        r_str = re.sub('[\[\]]', '', np.array2string(a=rm, prefix="  ", formatter=fm)) + "\n"
        t_str = re.sub('[\[\]]', '', np.array2string(a=tv, prefix="  ", formatter=fm)) + "\n"
        sg_op.append("   " + r_str + "-" * 40 + "\n   " + t_str)

    sg_str = "\n".join(str(x) for x in sg_op)
    return sg_str


def find_trans_matrix(big_cell, min_cell) -> str:
    from pymatgen.analysis.structure_matcher import StructureMatcher
    tm_str = ["PRIMITIVE TO GIVEN CELL"]
    fm = {'float_kind': lambda x: "%.6f" % x}
    sm = StructureMatcher(attempt_supercell=True, allow_subset=True, scale=True, primitive_cell=False)
    trans = sm.get_transformation(struct1=big_cell, struct2=min_cell)
    sc_str = re.sub('[\[\]]', '', np.array2string(a=trans[0], prefix="  ", formatter=fm)) + "\n"
    tr_str = re.sub('[\[\]]', '', np.array2string(a=trans[1], prefix="  ", formatter=fm)) + "\n"
    tm_str.append("   " + sc_str + "-" * 40 + "\n   " + tr_str)
    c_string = "\n".join(str(x) for x in tm_str)
    return c_string


def cli_run(argv) -> None:
    """
    Wrapper for the above commands, features a lot of printing from pymatgen made objects.
    """

    global c_log

    parser = argparse.ArgumentParser(description=symm_info.__doc__)  # Parser init
    parser.add_argument("poscar", type=str, default="POSCAR", help="location of poscar file")
    parser.add_argument("-sg", dest="sg", action="store_true",
                        help="Whether to dump space group information")
    parser.add_argument("--prim", dest="prim_cell", action="store_true",
                        help="Whether to dump the matrix transformation to primitive cell")
    parser.add_argument("--conv", dest="conv_cell", action="store_true",
                        help="Whether to dump the matrix transformation to conventional cell")
    parser.add_argument("-tm", dest="tm", action='store_true',
                        help="Whether to determine operations to convert primitive cell to supplied cell")

    parser.add_argument("-d", "--debug", dest="debug", action="store_true", help="Prints debug info")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="Prints verbose output")
    parser.add_argument("-q", "--quiet", dest="quiet", action="store_true", help="Quietens the space group operations")

    args = parser.parse_args(argv)

    if args.debug:  # Always include method for switching verbosity
        c_log.setLevel(logging.DEBUG)
    if args.verbose:
        c_log.setLevel(logging.INFO)
    c_log.debug(args)

    structure = Structure.from_file(args.poscar)
    sg = symm_info(structure=structure)

    if not args.quiet:
        print(operations_to_str(sg))

    if args.sg:
        print(f"Crystal System: {sg.get_crystal_system()}\n"
              f"Hall Symbol: {sg.get_hall()}\n"
              f"Lattice type: {sg.get_lattice_type()}"
              f"Space Group: {sg.get_space_group_number()}  {sg.get_space_group_symbol()}\n")

    if args.prim_cell:
        print(Poscar(sg.get_primitive_standard_structure(), comment="HEADER: Primitive Cell"))
    if args.conv_cell:
        print(Poscar(sg.get_conventional_standard_structure(), comment="HEADER: Conventional Cell"))

    if args.tm:
        c_string = find_trans_matrix(big_cell=structure, min_cell=sg.get_primitive_standard_structure())
        print(c_string)


if __name__ == "__main__":
    cli_run(sys.argv[1:])
