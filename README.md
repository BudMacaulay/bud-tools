# bud-tools
Useful tools written for vasp manipulation.

# PreReqs
```
- Python 3.7
- Pymatgen
```
# Installing pymatgen 
```
pip install pymatgen
```

Currently added:
| **script**     | **Input** | **Output**          | **Note**                                    | 
|----------------|-----------|---------------------|---------------------------------------------|
| make_spincar   | CHGCAR    | SPINCAR string      | Output is a spin density file               |
| make_supercell | POSCAR    | POSCAR string       | N/A                                         |
| make_surface   | POSCAR    | slabs/POSCARs       | makes a slab.json for further manipulation  |
| scale_abc      | POSCAR    | POSCAR string       | scales by % equally in all dir              |
| scale_to_volume| POSCAR    | POSCAR string       | scales a structure equally to a new volume  |
| stretch_cell   | POSCAR    | POSCAR string       | stretches one lattice vec w/ discrimination |
| element_subs   | POSCAR    | superstruct/POSCARs | elementwise substitution                    |

They should be all well documented and fairly flexible
