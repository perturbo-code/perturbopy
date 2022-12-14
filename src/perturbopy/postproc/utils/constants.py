prefixes = {'m': 1000, 'k': 0.001}


def energy_conversion_factor(initial_units, final_units):
   energy_equiv_units = {'ev': ['electron-volt', 'electronvolt', 'electronvolts', 'electron-volt'],
                         'Ha': ['hartree', 'Eh', 'E_h', 'hartrees'],
                         'J': ['Joules']}

   energy_units = {'ev': 27.2114, 'Ha': 1, 'J': 4.3597438e-18}
   energy_units_keys = energy_units.keys()

   initial_units = standard_units_name(initial_units, energy_equiv_units)
   final_units = standard_units_name(final_units, energy_equiv_units)

   return energy_units[final_units] / energy_units[initial_units]


def standard_units_name(units, equiv_units_names):
   units_symbol = units
   allowed_units_names = equiv_units_names.keys()

   for equiv_units_name in equiv_units_names:
      if units.lower() == equiv_units_name.lower():
         units_symbol = equiv_units_name
      else:
         for name in equiv_units_names[equiv_units_name]:
             if units.lower() == name.lower():
                 units_symbol = equiv_units_name

   if units_symbol not in allowed_units_names:
      raise Exception("Please choose units from the following list: {allowed_units_names}")

   return units_symbol


def hbar(energy_unit):
   hbar_dict = {'ev*s': 6.582119569e-16, 'atomic': 1, 'J*s': 1.054571817e-34}
   hbar_units_keys = hbar_dict.keys()

   if energy_unit not in hbar_units_keys:
      raise Exception("Please choose hbar units from the following list: {hbar_units_keys}")

   return None
