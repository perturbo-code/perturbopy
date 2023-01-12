

energy_units_names = {'eV': ['ev', 'electron-volt', 'electronvolt', 'electronvolts', 'electron-volts'],
                      'Ha': ['ha', 'hartree', 'eh', 'e_h', 'hartrees'],
                      'J': ['j', 'joule', 'joules'],
                      'Ry': ['ry', 'rydberg', 'rydbergs']}

energy_units_vals = {'eV': (2.7211396132, 1), 'Ha': (1, 0), 'J': (4.359748199, -18), 'Ry': (0.5, 0)}
prefix_exps_dict = {'y': -24, 'z': -21, 'a': -18, 'f': -15,
                    'p': -12, 'n': -9, 'mu': -6, 'm': -3,
                    'c': -2, 'd': -1, 'da': 1, 'h': 2,
                    'k': 3, 'M': 6, 'G': 9, 'T': 12,
                    'P': 15, 'E': 18, 'Z': 21, 'Y': 24}
length_units_names = {'bohr': ['bohr', 'a.u', 'atomic units', 'au'], 'angstrom': ['angstrom, a'], 'm': ['m', 'meter']}

length_units_vals = {'bohr': (1, 0), 'angstrom': (0.529177249, 0), 'm': (5.29177249, -11)}


def prefix_exp(prefix):

   if prefix == '':
      return 0
   else:
      if prefix not in prefix_exps_dict.keys():
         raise ValueError(f"Please choose prefixes from the following list: {list(prefix_exps_dict.keys())}")

      return prefix_exps_dict[prefix]


def prefix_conversion_exp(prefix):
   return -1 * prefix_exp(prefix)


def find_prefix_and_root_units(user_input_units, units_dict):
   '''

   milli-electron-Volt is units
   milli is prefix
   electron-Volt is units_names[]

   suggestion of names: units -> user_input_units
   units_names -> units_dict

   Put an example of how it works


   '''
   
   user_input_units = user_input_units.replace(' ', '').replace('-', '')

   for units_name in units_dict.keys():
      for name_variation in units_dict[units_name]:
         if name_variation in user_input_units.lower():
            user_input_units_split = user_input_units.lower().split(name_variation)
            
            if len(user_input_units_split) == 2 and user_input_units_split[1] == '':

               prefix = user_input_units[:len(user_input_units_split[0])]
               standard_units_name = units_name

               return prefix, standard_units_name

   raise ValueError(f"Please choose units from the following list: {list(units_dict.keys())}")


def standardize_units_name(user_input_units, units_dict):
   prefix, units = find_prefix_and_root_units(user_input_units, units_dict)

   return prefix + units


def conversion_factor(init_units, final_units, units_names, units_vals):
   init_prefix, init_units = find_prefix_and_root_units(init_units, units_names)
   final_prefix, final_units = find_prefix_and_root_units(final_units, units_names)

   init_val = units_vals[init_units]
   final_val = units_vals[final_units]

   conversion_factor = (final_val[0] / init_val[0],
                       (final_val[1] + prefix_conversion_exp(final_prefix)) - (init_val[1] + prefix_conversion_exp(init_prefix)))

   return conversion_factor[0] * 10**(conversion_factor[1])


def energy_conversion_factor(init_units, final_units):
   
   return conversion_factor(init_units, final_units, energy_units_names, energy_units_vals)


def length_conversion_factor(init_units, final_units):
   
   return conversion_factor(init_units, final_units, length_units_names, length_units_vals)


def hbar(energy_unit):
   hbar_dict = {'ev*fs': (6.582119569, -1), 'ev*s': (6.582119569, -16), 'atomic': (1, 0), 'J*s': (1.054571817, -34)}

   if energy_unit not in hbar_dict.keys():
      raise ValueError(f"Please choose hbar units from the following list: {list(hbar_dict.keys())}")

   return hbar_dict[energy_unit]
