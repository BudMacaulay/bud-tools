#!/usr/bin/env python3
# coding: utf-8

import sys, argparse, logging

from pymatgen.io.vasp.sets import MPMetalRelaxSet, MPRelaxSet, _load_yaml_config
from pymatgen.io.vasp.inputs import Incar
from pymatgen.core import Structure

# Adopted format: level - current function name - mess. Width is fixed as visual aid
c_log = logging.getLogger(__name__)
std_format = '[%(levelname)5s - %(funcName)10s] %(message)s'
logging.basicConfig(format=std_format)
c_log.setLevel(logging.WARNING)


class BtRelaxUnknownSet(MPRelaxSet):
    """
    Makes a vasp calculation set using pymatgen auto incar / kpoints stuff..


    Notes:
        The EDIFF variable is ridicolously loose. I have redefined this to be a just a
        little more strict;
                EDIFF = 0.0002  ->  EDIFF = 1E-05

        The ISMEAR variable is notoriously finnicky if the system is metallic, semiconducting etc.
        In which:
                metallic systems require:           ISMEAR = 1 or ISMEAR = 2 ; SIGMA = 0.2
                small semiconducting sys require:   ISMEAR = -5 ; SIGMA = 0.2
                large semiconducting sys require:   ISMEAR = 0 ; SIGMA 0.05

        There is no real way to tell if your system is an of these from inspection.

        This class sets the ISMEAR, SIGMA variables to the vasp recommended for unknown systems:
            Current VASP guidelines is to set ISMEAR = 0 ; SIGMA = 0.03

        This class also tuned the KSpacing to be a little tighter incase the system is metallic
    """

    COMFIG = _load_yaml_config("MPRelaxSet")

    def __init__(self, structure, **kwargs):
        """
        :param structure: Structure
        param kwargs: Those from dictset
        """
        super().__init__(structure, **kwargs)
        self._config_dict["INCAR"].update({"ISMEAR": 0, "SIGMA": 0.05})
        self._config_dict["INCAR"].update({"EDIFF": 0.00001})

        self._config_dict["KPOINTS"].update({"reciprocal_density": 200})


class BtRelaxMetalSet(BtRelaxUnknownSet):
    """
    Makes a vasp calculation set using pymatgen auto incar / kpoints stuff..


    Notes:
        The EDIFF variable is ridicolously loose. I have redefined this to be a just a
        little more strict;
                EDIFF = 0.0002  ->  EDIFF = 1E-05

        This class sets the ISMEAR, SIGMA variables to the vasp recommended for metal systems:
            Current VASP guidelines is to set ISMEAR = 0 ; SIGMA = 0.20

        This class also tuned the KSpacing to be a little tighter.
    """

    def __init__(self, structure, **kwargs):
        """
        :param structure: Structure
        :param kwargs: Same as those supported by DictSet.
        """
        super().__init__(structure, **kwargs)
        self._config_dict["INCAR"].update({"ISMEAR": 1, "SIGMA": 0.2})
        self._config_dict["KPOINTS"].update({"reciprocal_density": 200})
        self.kwargs = kwargs


class BtRelaxInsulSet(BtRelaxUnknownSet):
    """
    Makes a vasp calculation set using pymatgen auto incar / kpoints stuff..


    Notes:
        The EDIFF variable is ridicolously loose. I have redefined this to be a just a
        little more strict;
                EDIFF = 0.0002  ->  EDIFF = 1E-05

        This class sets the ISMEAR, SIGMA variables to the vasp recommended for insulating systems:
            Current VASP guidelines is to set ISMEAR = -5 ; SIGMA = 0.20

        This class also tuned the KSpacing to be a little tighter.
    """

    def __init__(self, structure, **kwargs):
        """
        :param structure: Structure
        :param kwargs: Same as those supported by DictSet.
        """
        super().__init__(structure, **kwargs)
        self._config_dict["INCAR"].update({"ISMEAR": -5, "SIGMA": 0.2})
        self._config_dict["KPOINTS"].update({"reciprocal_density": 200})
        self.kwargs = kwargs


def sort_incar_flags(incar: Incar):
    """
    Method to sort the incar flags (from the typical alphabetical to a much more reader friendly form)
    Helps quite a lot with readibility
    Some interesting decisions on how to sort flags
    General order is:
    starting flags, writing flags, elecrelax flags, ion relax flags, performance flags, misc flags.

    """
    global c_log

    start_flags = ["ISTART", "ICHARG",
                   "INIWAV", "ISPIN", "MAGMOM", "LNONCOLLINEAR", "LSORBIT",
                   "LASPH", "METAGGA"]

    write_flags = ["NWRITE", "LWAVE", "LDOWNSAMPLE", "LCHARG", "LVTOT", "LVHAR", "LELF", "LORBIT"]
    erel_flags = ["ALGO", "PREC", "ENCUT", "ENINI", "ENAUG", "NELM", "EDIFF", "LMAXMIX", "ROPT"]
    erel_mixs = ["ISMEAR", "SIGMA", "IMIX", "AMIX", "BMIX", "AMIX_MAG", "BMIX_MAG"]
    ionic_flags = ["EDIFFG", "NSW", "IBRION", "ISIF", "ISYM", "POTIM", ]
    perf_flags = ["NCORE", "LREAL", "KPAR"]

    new_incar = incar
    for k, v in incar.items():
        if k in start_flags:
            new_incar[k] = (v, 0)
        elif k in write_flags:
            new_incar[k] = (v, 1)
        elif k in erel_flags:
            new_incar[k] = (v, 2)
        elif k in erel_mixs:
            new_incar[k] = (v, 3)
        elif k in ionic_flags:
            new_incar[k] = (v, 4)
        elif k.startswith("LDA"):
            new_incar[k] = (v, 5)
        elif k in perf_flags:
            new_incar[k] = (v, 6)
        else:
            new_incar[k] = (v, 7)

    new_dict = dict(sorted(new_incar.items(), key=lambda item: item[1][1]))
    f_dict = {k: v[0] for k, v in new_dict.items()}
    i = Incar.from_dict(f_dict)

    return i


def make_vasp_set(structure: Structure, fmt="unknown", ox_states=None,
                  user_incar_settings=None, user_kpoints_settings=None):
    """
    Make a vaspset from a structure,

    Current features:
     Adding your own user incar settings in form of adict
     Adding your own user kpoint settings

     Multiple system fmt (metal, insulator, unknown) specified by a string
     It will attempt to calculate the oxidation states and thus spin states for the structures.
     :)

    """

    if ox_states is None:
        structure.add_oxidation_state_by_guess()
    else:
        structure.add_oxidation_state_by_element(oxidation_states=ox_states)

    if fmt.lower().startswith("u"):
        vaspset = BtRelaxUnknownSet(structure=structure, user_incar_settings=user_incar_settings,
                                    user_kpoints_settings=user_kpoints_settings)
    elif fmt.lower().startswith("m"):
        vaspset = BtRelaxMetalSet(structure=structure, user_incar_settings=user_incar_settings,
                                  user_kpoints_settings=user_kpoints_settings)
    elif fmt.lower().startswith("i"):
        vaspset = BtRelaxInsulSet(structure=structure, user_incar_settings=user_incar_settings,
                                  user_kpoints_settings=user_kpoints_settings)
    else:
        c_log.warning(f"type set to: {fmt} this is not recommended")
        vaspset = BtRelaxUnknownSet(structure=structure, user_incar_settings=user_incar_settings,
                                    user_kpoints_settings=user_kpoints_settings)
    return vaspset


def cli_run(argv) -> None:
    """
    Wrapper for the above command, handles parsing of args and logging, to avoid mess
    """

    global c_log

    parser = argparse.ArgumentParser(description=make_vasp_set.__doc__)  # Parser init
    parser.add_argument("filename", type=str, default="POSCAR", help="location of the pymatgen structure")
    parser.add_argument("output_dir", type=str, default=".", help="location to create the vasp set")

    parser.add_argument("-f", "--fmt", dest="fmt", default="unknown", help="format of the desired incar")

    parser.add_argument("-o", "--ox_states", dest="ox_states", nargs="*",
                        default=None, help="oxidation states as space seperated key value pairs i.e: Li 1")

    parser.add_argument("-i", "--iflags", dest="incar_settings", nargs="*",
                        default=None, help="incar flags as space seperated key value pairs i.e: ENCUT 600")

    parser.add_argument("--kflags", dest="k_settings", nargs="*",
                        default=None, help="kpoint flags as space seperated key value paris i.e: mode line")

    parser.add_argument("--debug", dest="debug", action="store_true")  # Always have the verbose optional
    parser.add_argument("--verbose", dest="verbose", action="store_true")  # Always have the verbose optional

    args = parser.parse_args(argv)

    if args.debug:  # Always include method for switching verbosity
        c_log.setLevel(logging.DEBUG)
    if args.verbose:
        c_log.setLevel(logging.INFO)
    c_log.debug(args)


    structure = Structure.from_file(args.filename)
    vaspset = make_vasp_set(structure=structure, fmt=args.fmt,
                            ox_states=args.ox_states)

    vaspset.write_input(output_dir=args.output_dir,
                        make_dir_if_not_present=True, include_cif=True)

if __name__ == "__main__":
    cli_run(sys.argv[1:])
