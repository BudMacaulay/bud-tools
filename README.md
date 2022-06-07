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
| **script**         | **Input**   | **Output**          | **Note**                                   |  **Note2**    |
|--------------------|-------------|---------------------|--------------------------------------------|---------------|
| make_supercell     | POSCAR      | POSCAR string       | N/A                                        | N/A           |
| stretch_cell       | POSCAR      | POSCAR string       | Can stretch with discrimination            | N/A           |
| make_surface       | POSCAR      | slabs/POSCARs       | makes a slab.json for further manipulation | N/A           |
| freeze_slab_center | POSCAR/dict | POSCAR w/S.D        | adds selective dynamics to a slab struct   | Two methods   |
| make_spincar       | CHGCAR      | SPINCAR string      | Output is a spin density file              | N/A           |
| element_subs       | POSCAR      | superstruct/POSCARs | elementwise substitution                   | Not avail     |
| symminfo           | POSCAR      | SpaceGroup String   | Prints symmetry/transformation information | Multiple flags|

They should be all well documented and fairly flexible
