Utilities
=========

Constants
~~~~~~~~~

In the ``constants`` module, we store commonly used constants and provide tools for converting between units. 

The most useful functions are ``conversion_factor``, ``energy_conversion_factor``, and ``length_conversion_factor``. Most of the other functions are helper functions. 

The ``conversion_factor`` function takes in four inputs: ``init_units``, ``final_units``, ``units_names``, and ``units_vals`` to convert between ``init_units`` and ``final_units``. Both ``init_units`` and ``final_units`` can have prefixes and base units, described below.

The case-sensitive prefixes are defined in the ``prefix_exps_dict`` dictionary stored in the module. For example, the prefix 'c' (centi) corresponds to 1e-2, while prefix 'k' (kilo) corresponds to 1e3:

.. code-block :: python

    ppy.constants.prefix_exps_dict['c']
    >> -2
    ppy.constants.prefix_exps_dict['k']
    >> 3

Next, the case-insensitive base units of ``init_units`` and ``final_units`` are defined in the ``units_names`` dictionary. This dictionary defines a standard name chosen for each unit, as well as its possible variations. (Note we provide two predefined ``units_names`` dictionaries in the module: ``length_units_names`` and ``energy_units_names`` for converting between length and energy units, respectively.) For example, the unit 'meter' could be written as 'm' or 'meter'. We choose 'm' as the standard name, but would like our functions to recognize 'meter' as well. Therefore, we put the following into ``length_units_names``:

.. code-block :: python

    ppy.constants.length_units_names['m']
    >> ['m', 'meter']

The full ``length_units_names`` and ``energy_units_names`` dictionaries are:

.. code-block :: python

    >> {'bohr': ['bohr', 'a.u', 'atomic units', 'au'], 'angstrom': ['angstrom, a'], 'm': ['m', 'meter']}

Finally, ``units_vals`` is a dictionary that provides a value for each standard base units. Again, we provide two predefined ``units_vals`` dictionaries: ``length_units_vals`` and ``energy_units_vals``. For example, for lengths, possible units include 'bohr' and 'angstrom'. We set 'bohr' to 1, and the remaining values are the conversion factors between different units and Hartrees. Note these values are stored in a tuple (value, exponent).

.. code-block :: python

    ppy.constants.length_units_vals
    >> {'bohr': (1, 0), 'angstrom': (0.529177249, 0), 'm': (5.29177249, -11)}

To get the conversion factor between length units, we can therefore do the following:

.. code-block :: python

    ppy.constants.conversion_factor('fm', 'cm', ppy.constants.length_units_names, ppy.constants.length_units_vals)
    >> 1e-13
    ppy.constants.conversion_factor('a.u', 'bohr', ppy.constants.length_units_names, ppy.constants.length_units_vals)
    >> 1.0
    ppy.constants.conversion_factor('a.u', 'angstrom', ppy.constants.length_units_names, ppy.constants.length_units_vals)
    >> 0.529177249

This function is most helpful if you need to convert between units that are not provided in the standard ``length_units_vals`` or ``energy_units_vals`` dictionaries. Otherwise, you can use the ``energy_conversion_factor``, and ``length_conversion_factor`` functions, which do not require the ``units_names`` and ``units_vals`` inputs.

.. code-block :: python

    ppy.constants.length_conversion_factor('fm', 'cm')
    >> 1e-13
    ppy.constants.length_conversion_factor('a.u', 'angstrom')
    >> 0.529177249

Finally, we also provide a function ``hbar`` that outputs the value of the reduced Planck's constant in different units. Similar functions could be implemented for other constants with units.

.. code-block :: python

    ppy.constants.hbar('ev*fs')
    >> 0.6582119569
