prefix_names = {'y':'yocto', 'z':'zepto', 'a':'atto', 'f':'femto',
                  'p':'pico', 'n':'nano', 'mu':'micro', 'm':'milli',
                  'c':'centi', 'd':'deci', '':'', 'da':'deka', 'h':'hecto',
                  'k':'kilo', 'M':'mega', 'G':'giga', 'T':'tera',
                  'P':'peta', 'E':'exa', 'Z':'zetta', 'Y':'yotta'}

def standardize_prefix_name(prefix):
   standard_prefix = None

   for prefix_name in prefix_names:
      if (prefix == prefix_name) or (prefix.lower() == prefix_names[prefix_name]):
         standard_prefix = prefix_name

   if standard_prefix is None:
      prefix_names_str = [str(name) for name in prefix_names.keys()]
      raise ValueError(f"Please choose prefix from the following list: {prefix_names_str}")

   return standard_prefix

def prefix_conversion_factor(prefix):

   if prefix == '':
      conversion_factor = 1
   else:
      if prefix not in prefix_names.keys():
         prefix = standardize_prefix_name(prefix)

      prefix_vals = {}
      current_prefix_exp = -24
      for prefix_name in prefix_names.keys():
         prefix_vals[prefix_name] = 10**(current_prefix_exp)
         if (current_prefix_exp  >=-3) and (current_prefix_exp < 3):
            current_prefix_exp += 1
         else:
            current_prefix_exp += 3
      conversion_factor = 1 / prefix_vals[prefix]

   return conversion_factor

def find_prefix_and_root_units(units, units_names):
   units = units.replace(' ', '').replace('-', '')

   standard_units_name = None
   standard_prefix = ''

   for name in units_names.keys():
      if units.lower() in units_names[name]:
         standard_units_name = name
      else:
         for name_variation in units_names[name]:
            if name_variation in units.lower() and units.lower().split(name_variation)[1] == '':
               try:
                  prefix = units.lower().split(name_variation)[0]
                  
                  if len(prefix) == 1:
                     prefix = units[0]

                  standard_prefix = standardize_prefix_name(prefix)
                  standard_units_name = name
               except ValueError:
                  pass

   if standard_units_name is None:
      units_names_str = [str(name) for name in units_names.keys()]
      raise ValueError(f"Please choose units from the following list: {units_names_str}")

   return standard_prefix, standard_units_name

def standardize_units_name(units, units_names):
   prefix, units = find_prefix_and_root_units(units_names, units_names)

   return prefix + units

def energy_conversion_factor(initial_units, final_units):
   energy_units_names = {'eV': ['ev', 'electron-volt', 'electronvolt', 'electronvolts', 'electron-volts'],
                         'Ha': ['ha', 'hartree', 'eh', 'e_h', 'hartrees'],
                         'J': ['j', 'joule', 'joules'],
                         'Ry':['ry', 'rydberg', 'rydbergs']}

   energy_units_vals = {'eV': 27.2114, 'Ha': 1, 'J': 4.3597438e-18, 'Ry':0.5}
   
   energy_units_keys = energy_units_vals.keys()

   initial_prefix, initial_units = find_prefix_and_root_units(initial_units, energy_units_names)
   final_prefix, final_units = find_prefix_and_root_units(final_units, energy_units_names)

   conversion_factor = (energy_units_vals[final_units] * prefix_conversion_factor(final_prefix)) \
                     / (energy_units_vals[initial_units] * prefix_conversion_factor(initial_prefix))
   
   return conversion_factor

def hbar(energy_unit):
   hbar_dict = {'ev*s': 6.582119569e-16, 'atomic': 1, 'J*s': 1.054571817e-34}
   hbar_units_keys = hbar_dict.keys()

   if energy_unit not in hbar_units_keys:
      raise Exception("Please choose hbar units from the following list: {hbar_units_keys}")

   return None
