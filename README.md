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
| **script**     | **Input** | **Output**          | **Note**                                   | 
|----------------|-----------|---------------------|--------------------------------------------|
| make_supercell | POSCAR    | POSCAR string       | N/A                                        |
| stretch_cell   | POSCAR    | POSCAR string       | Can stretch with discrimination            |
| make_surface   | POSCAR    | slabs/POSCARs       | makes a slab.json for further manipulation |
| make_spincar   | CHGCAR    | SPINCAR string      | Output is a spin density file              |
| element_subs   | POSCAR    | superstruct/POSCARs | elementwise substitution                   |

They should be all well documented and fairly flexible
