import numpy as np
from perturbopy.postproc.dbs.phys_quantity_array import PhysQuantityArray

class TensorPhysQuantityArray(PhysQuantityArray):

    def __getitem__(self, index):

        xyz_to_int = {'xx':(0, 0), 'xy':(0, 1), 'xz':(0, 2),
                      'yx':(1, 0), 'yy':(1, 1), 'yz':(1, 2),
                      'zx':(2, 0), 'zy':(2, 1), 'zz':(2, 2)}

        # Customize the indexing behavior here
        if isinstance(index, str) and index.lower() in xyz_to_int.keys():
            print(xyz_to_int[index.lower()])
            return super().__getitem__(xyz_to_int[index.lower()])
        else:
            return super().__getitem__(index)