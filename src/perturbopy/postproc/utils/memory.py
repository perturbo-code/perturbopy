"""
Memory management utilities
"""

import sys
import numpy as np


def get_size(array, name='array', dump=True):
    """
    Get size of an array in MB

    Parameters
    ----------
    array : numpy array
        Array.

    name :
        Name of array, optional.

    dump :
        Specifies whether to print out or not the size

    Returns
    -------
    size : float
        Size in MB.
    """

    # Check if the array is a numpy array and calculate size accordingly
    if isinstance(array, np.ndarray):
        # Calculate size in bytes for numpy array
        size_bytes = array.size * array.itemsize
    else:
        # Use sys.getsizeof() for other types of arrays
        size_bytes = sys.getsizeof(array)

    size_kb = size_bytes / 1024.0

    if size_kb < 1024.0:

        size = size_kb
        unit = 'KB'

    elif size_kb / 1024.0 < 1024.0:

        size_mb = size_kb / 1024.0
        size = size_mb
        unit = 'MB'

    else:

        size_gb = size_kb / 1024.0**2
        size = size_gb
        unit = 'GB'

    if dump:
        print(f'===Size of {name:<10} {str(array.shape):<12} {str(array.dtype):<8}: {size:6.3f} {unit}')

    return size, unit
