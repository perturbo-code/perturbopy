EphmatSpin tutorial
===============

In this section, we describe how to use Perturbopy to process a Perturbo ``'ephmat_spin'`` calculation. 

The ``'ephmat_spin'`` calculation computes absolute values of the e-ph spin-flip matrix elements, summed over the number of electronic bands, given two lists of k-points and q-points. We first run the Perturbo calculation following the instructions on the Perturbo website and obtain the YAML file, *'diam_ephmat_spin.yml'*. For more information, please refer to the `Perturbo website <https://perturbo-code.github.io/mydoc_spin.html#e-ph-spin-flip-matrix-elementscalc_mode--ephmat_spin>`_. 

Next, we create the :py:class:`.EphmatSpin` object using the YAML file as an input. This object contains all of the information from the YAML file.

.. code-block :: python

    import perturbopy.postproc as ppy

    # Example using the ephmat_spin calculation mode.
    diam_ephmat_spin = ppy.EphmatSpin.from_yaml('diam_ephmat_spin.yml')

Accessing the data
~~~~~~~~~~~~~~~~~~

The attributes in an :py:class:`.EphmatSpin` object have the same name and format as an object from the :py:class:`.Ephmat`. The k-points are stored in :py:attr:`.EphmatSpin.kpt`, which is a :py:class:`RecipPtDB` object. The data for the phonons is stored analogously in :py:attr:`.EphmatSpin.qpt` (another :py:class:`RecipPtDB` object) and :py:attr:`EphmatSpin.phdisp`, a :py:class:`UnitsDict` object where the keys are the phonon mode and the values are the phonon energies computed across the q-points.

.. code-block :: python
    
    # Access the k-point coordinates. There is only one in this calculation.
    # The units are in crystal coordinates.
    diam_ephmat_spin.kpt.points
    >> array([[0.],
              [0.],
              [0.]])

    diam_ephmat_spin.kpt.units
    >> 'crystal'

    # There are 196 q-point coordinates (we display the first two below).
    # The units are in crystal coordinates.
    diam_ephmat_spin.qpt.points.shape
    >> (3, 196)

    diam_ephmat_spin.qpt.points[:, :2]
    >> array([[0.5   , 0.4902],
              [0.5   , 0.4902],
              [0.5   , 0.4902]])

    diam_ephmat_spin.qpt.units
    >> 'crystal'

    # Access the phonon energies, which are a UnitsDict.
    # There are 6 modes, which are the keys of the dictionary.
    diam_ephmat_spin.phdisp.keys()
    >> dict_keys([1, 2, 3, 4, 5, 6])

    # Phonon energies of the first 2 q-points in phonon mode 3.
    diam_ephmat_spin.phdisp[3][:2]
    >> array([130.41105408, 130.31173133])

    diam_ephmat_spin.phdisp.units
    >> 'meV'

Please see the section :ref:`handling_kpt_qpt` for more details on accessing information from :py:attr:`.EphmatSpin.kpt` and :py:attr:`.EphmatSpin.qpt`, such as labeling the k, q-points and converting to Cartesian coordinates.

The ``'ephmat_spin'`` calculation interpolates the deformation potentials and e-ph elements from the spin-flip process which are stored in dictionaries :py:attr:`.EphmatSpin.defpot` and :py:attr:`.EphmatSpin.ephmat`, respectively. Both are :py:class:`UnitsDict` objects. The keys represent the phonon mode, and the values are (num_kpoints x num_qpoints) size arrays.

.. code-block :: python

    # There are 6 keys, one for each mode.
    diam_ephmat_spin.ephmat.keys()
    >> dict_keys([1, 2, 3, 4, 5, 6])

    # There is 1 k-point and 196 q-points, so the e-ph matrix is 1 x 196.
    diam_ephmat_spin.ephmat[1].shape
    >> (1, 196)

    # The e-ph spin-flip matrix elements corresponding to the first
    # phonon mode, first (and only) k-point, and first two q-points.
    diam_ephmat_spin.ephmat[1][0, :2]
    >> array([[5.37973306e-06, 2.51372197e+00]])

    # Units for the e-ph spin-flip matrix elements are in meV.
    diam_ephmat_spin.ephmat.units
    >> 'meV'

    # We can extract analogous information from the deformation potential.
    diam_ephmat_spin.defpot[1].shape
    >> (1, 196)

    # Units for the deformation potential are in eV/A.
    diam_ephmat_spin.defpot.units
    >> 'eV/A'

Plotting the data
-----------------

Please refer to the :ref:`ephmat_tutorial` for details on plotting the data.
