#!/usr/bin/env python3
# coding: utf-8

import sys, argparse, logging, json, math, time
from monty.json import MontyEncoder

from scipy.cluster.vq import kmeans
from pymatgen.core import Structure
from pymatgen.core.surface import Slab
from pymatgen.io.vasp import Poscar
from pymatgen.analysis.adsorption import AdsorbateSiteFinder

# Adopted format: level - current function name - mess. Width is fixed as visual aid
c_log = logging.getLogger(__name__)
std_format = '[%(levelname)5s - %(funcName)10s] %(message)s'
logging.basicConfig(format=std_format)
c_log.setLevel(logging.WARNING)


def get_layer_count_from_structure(structure, dimension=2, layer_tol=0.25):
    """
    Faster method to determine surface sites that doesnt use pymatgens heavy
    voronio generation. Will perhaps maybe die in edge cases and the cases in which layers arent CLEARLY distinct in c.
    If calling this results in a incorrectly S.D'd slab i suggest you fiddle with layer_tol
    """
    across_dim = structure.cart_coords[:, dimension]
    across_dim.sort()

    groups = [[across_dim[0]]]
    count = 0
    for dim_coord in across_dim:
        if dim_coord not in groups[count]:
            if not abs(dim_coord - groups[count][0]) < layer_tol:
                count += 1
                groups.append([])
            groups[count].append(dim_coord)
    return len(groups)


def frz_central_slab(slab: Slab, frz_prop=0.30) -> Slab:
    """
    Tool to freeze the central layers on a large slab calculation (as they will repr the bulk)
    in a bid to massively reduce the total degrees of freedom per ionic step.

    If loaded structure is a Structure not a slab then it will call get_layer_count
    The pymatgen get_surface_sites
     call is suprisingly costly and thus methods of avoiding calling this would be great.

     First idea is to group sites by C and then delta C between sites.
     This will first order sites via C and then try and distinguish layers.

    """
    if type(slab) == Slab:  # This method is very costly (10 seconds for 40 atom systems)
        t = time.time()
        surface_sites = slab.get_surface_sites()
        total_layers = (len(slab) / len(surface_sites["top"]))
        t2 = time.time()
        c_log.debug(f"Function call get_surface_sites took: {round(t2 - t, 3)} seconds?!")
    elif type(slab) == Structure:  # Quicker but perhaps less reliable
        c_log.info(f"input file has been opened as: {type(slab)}, This may speed things up at a risk")
        total_layers = get_layer_count_from_structure(structure=slab, dimension=2, layer_tol=0.25)
    else:
        c_log.warning(f"Something went seriously wrong")
        return

    bl = total_layers * frz_prop  # Method to ensure SD is symmetric across the slab
    if total_layers % 2:  # if layers odd
        if math.floor(bl) % 2:  # Make bulk odd
            bl = math.floor(bl)
        else:
            bl = math.ceil(bl)
    else:  # if layers even
        if math.floor(bl) % 2:  # make bulk even
            bl = math.ceil(bl)
        else:
            bl = math.floor(bl)
    sl = total_layers - bl
    c_log.debug(f"bl: {bl}, total: {total_layers}, sl: {sl}")

    atoms_per_layer = len(slab) / total_layers
    c_sort_coords = []
    for (n, x) in enumerate(slab.frac_coords[:, 2]):
        c_sort_coords.append((n, x))
    c_sort_coords.sort(key=lambda p: p[1])

    dyn = int(atoms_per_layer * (sl / 2))
    bot_idx = [x[0] for x in c_sort_coords[:dyn]]
    c_sort_coords.reverse()
    top_idx = [x[0] for x in c_sort_coords[:dyn]]
    c_log.debug(f"Number of dyn atoms: top: {len(top_idx)}, bottom: {len(bot_idx)}")

    sel_dyn = [[False, False, False]] * len(slab)
    sel_dyn = [[True, True, True] if n in bot_idx + top_idx else x for n, x in enumerate(sel_dyn)]
    slab.add_site_property(property_name="selective_dynamics", values=sel_dyn)

    return slab


def cli_run(argv) -> None:
    """
    Wrapper for the above command, handles parsing of args and logging, to avoid mess
    """

    global c_log

    parser = argparse.ArgumentParser(description=frz_central_slab.__doc__)  # Parser init
    parser.add_argument("slab_file", type=str, default="slab.dict", help="PositionalArgument")
    parser.add_argument("-f", "--fast", dest="fast", action="store_true",
                        help="Use fast method of determining number of layers")

    parser.add_argument("-p" "--prop", dest="frz_prop", type=float, default=0.35,
                        help="% amount of slab to freeze (centre outward) good value is around 4 layers of bulk")
    parser.add_argument("--debug", dest="debug", action="store_true")  # Always have the debug optional
    parser.add_argument("--verbose", dest="verbose", action="store_true")  # Always have the verbose optional

    args = parser.parse_args(argv)

    if args.debug:  # Always include method for switching verbosity
        c_log.setLevel(logging.DEBUG)
    if args.verbose:
        c_log.setLevel(logging.INFO)
    c_log.debug(args)

    if args.fast or not args.slab_file.endswith("json"): # Use the fast method.
        slab = Structure.from_file(filename=args.slab_file)
    else:
        f = open(args.slab_file)
        d = json.load(f)
        slab = Slab.from_dict(d=d)

    dyn_slab = frz_central_slab(slab, args.frz_prop)
    print(Poscar(dyn_slab, selective_dynamics=dyn_slab.site_properties["selective_dynamics"]))


if __name__ == "__main__":
    cli_run(sys.argv[1:])
