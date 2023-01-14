import numpy as np
from perturbopy.postproc.utils.constants import standardize_units_name
from perturbopy.postproc.utils.lattice import cryst_to_cart, reshape_kpts

kpt_units_names = {'cartesian': ['tpiba', 'cartesian', 'cart'], 'crystal': ['crystal', 'cryst', 'frac', 'fractional']}


class KptsDB():
   """
   This is a class representation of a set of k-points in reciprocal space.

   Parameters
   ----------
   kpts_cart : array
      array of k-points in Cartesian coordinates, in units of 2pi/a

   kpts_cryst : array
      array of k-points in crystal coordinates

   _units : str
      the units calculations will be performed in (crystal or cartesian).
      Example: if _units = 'crystal', then kpts_cryst will be used when
      a method such as "compute_kpt_distances" is called on the KptsDB object.

   kpath : array
      array of values corresponding to each k-point, for plotting purposes

   kpath_units : str
      units of the kpath points, typically arbitrary

   labels : dict
      dictionary of k-point labels
      example: {"Gamma": [0, 0, 0], 'L': [.5,.5,.5]}

   """

   def __init__(self, kpts_cart, kpts_cryst, units='crystal', kpath=None, kpath_units='arbitrary', labels={}):

      """
      Constructor method

      """
      self.kpts_cart = reshape_kpts(kpts_cart)
      self.kpts_cryst = reshape_kpts(kpts_cryst)
      self._units = standardize_units_name(units, kpt_units_names)

      if kpath is None:
         self.kpath = np.arange(0, np.shape(kpts_cart)[1])
      else:
         self.kpath = kpath

      self.kpath_units = kpath_units
      self.labels = labels

   @classmethod
   def from_lattice(self, kpts, units, lat, recip_lat, kpath=None, kpath_units='arbitrary', labels={}):
      """
      Class method to create a KptsDB from one set of k-points and the lattice information.

      Parameters
      ----------
      Parameters
      ----------
      kpts : array
         array of k-points in Cartesian or crystal coordinates

      units : str
         the units kpts are given in

      lat : array
         3x3 array of lattice vectors [v1, v2, v3] in units of alat

      recip_lat : array
         3x3 array of reciprocal lattice vectors [v1, v2, v3] in units of
         2pi/a

      kpath : array
         array of values corresponding to each k-point, for plotting purposes

      kpath_units : str
         units of the kpath points, typically arbitrary

      labels : dict
         dictionary of k-point labels
         example: {"Gamma": [0, 0, 0], 'L': [.5,.5,.5]}

      Returns
      -------
      kpts_db : KptsDB
         the KptsDB created from the lattice information and k-points
      """
      units = standardize_units_name(units, kpt_units_names)
      
      if units == 'cartesian':
         kpts_cart = reshape_kpts(kpts)
         kpts_cryst = cryst_to_cart(kpts_cart, lat, recip_lat, forward=False, real_space=False)

      elif units == 'crystal':

         kpts_cryst = reshape_kpts(kpts)
         kpts_cart = cryst_to_cart(kpts_cryst, lat, recip_lat, forward=True, real_space=False)
      else:
         return None

      return KptsDB(kpts_cart, kpts_cryst, units, kpath, kpath_units, labels)

   @property
   def units(self):
      """
      Property storing the units that calculations will be performed in, i.e.
      cartesian or crystal.

      Returns
      -------
      self._units : str

      """
      return self._units

   @units.setter
   def units(self, new_units):
      """
      Setter for the units property.

      Parameters
      ----------
      new_units : str
         The value to which the _units attribute should be changed

      """
      self._units = standardize_units_name(new_units, kpt_units_names)

   def kpts_from_units(self, units):
      """
      Method that returns k-points according to the specified units.

      Parameters
      ----------
      units : str
         The units k-points should be returned in

      Returns
      -------
      kpts : the k-points in the specified units

      """
      units = standardize_units_name(units, kpt_units_names)

      if units == 'cartesian':
         return self.kpts_cart
      elif units == 'crystal':
         return self.kpts_cryst
      else:
         return None
   
   @property
   def kpts(self):
      """
      Property storing the k-points corresponding to the units property.
      i.e. if self.units = "crystal", then kpts_cryst will be returned.
      If self.units = "cartesian", then kpts_cart will be returned.

      Returns
      -------
      kpts : array
         the k-points corresponding the units property

      """
      return self.kpts_from_units(self.units)

   def scale_kpath(self, range_min, range_max):
      """
      Method to scale the arbitrary k path plotting coordinates to a certain range.

      Parameters
      ----------
      range_min: float
         Lower limit of the range to which the k path coordinates will be scaled.

      range_max: float
         Upper limit of the range to which the k path coordinates will be scaled.

      Returns
      -------
      None

      """

      self.kpath = (self.kpath - min(self.kpath)) \
                               / (max(self.kpath) - min(self.kpath)) \
                               * (range_max - range_min) \
                               + range_min

   def compute_kpt_distances(self, kpt):
      """
      Method to compute the distances between each k-point in the kpts property
      and an inputted k-point

      Parameters
      ----------
      kpt : array
         The k-point that distances will be computed from

      Returns
      -------
      distances : array
         an array of distances between each k-point in the kpts property and kpt

      """
      kpt = reshape_kpts(kpt)
      distances = np.linalg.norm(self.kpts - np.array(kpt), axis=0)
      
      return distances

   def find_kpt(self, kpt, nearest=True, **kwargs):
      """
      Method to find the index or indices of a particular kpt

      Parameters
      ----------
      kpt: array
         The k-point to be searched

      nearest: bool
         If true, the index of the closest k-point closest to the kpt input
         will be returned

      Returns
      -------
      kpt_indices: list
         The indices of the matching k-point in the kpts array

      """
      atol = kwargs.pop('atol', 1e-16)
      rtol = kwargs.pop('rtol', 1e-10)

      distances = self.compute_kpt_distances(kpt)
      kpt_indices = np.where(np.isclose(distances, 0, atol=atol, rtol=rtol))[0]
      
      if len(kpt_indices) == 0:
         if nearest:
            min_distance = np.amin(distances)
            kpt_indices = np.where(np.isclose(distances, min_distance, atol=atol, rtol=rtol))[0]

            print(f"Nearest kpt to {kpt} is {self.kpts[:,kpt_indices[0]]}")
         else:
            raise ValueError("k-point is not in the list of k-points")

      return kpt_indices

   def kpt_to_kpath(self, kpt, nearest=True):
      """
      Method to find the k-path coordinate corresponding to a k-point coordinate

      Parameters
      ----------
      kpt: list
         The k-point to be searched

      nearest: bool
         If true, the k-path coordinate of the k-point closest to the kpt input will
         be returned

      Returns
      -------
      kpath_coord: array
         The k-path coordinates of the corresponding k-point(s)

      """

      kpath_coord = self.kpath[self.find_kpt(kpt, nearest)]

      return kpath_coord

   def kpath_to_kpt(self, kpath, nearest=True, **kwargs):
      """
      Method to find the k-point corresponding to a k-path coordinate

      Parameters
      ----------
      kpt: list
         The k-path to be searched

      nearest: bool
         If true, the kpt of the closest k-path coordinate will be returned

      Returns
      -------
      kpath_coord: list
         The k-point(s) of the corresponding k-path coordinate

      """
      atol = kwargs.pop('atol', 1e-16)
      rtol = kwargs.pop('atol', 1e-10)

      if kpath in self.kpath:
         kpath_idx = np.isclose(self.kpath, kpath)
      else:
         if nearest:
            distances = np.abs(self.kpath - kpath)
            min_distance = np.amin(distances)
            kpath_idx = np.where(np.isclose(distances, min_distance, atol=atol, rtol=rtol))[0]
         else:
            raise ValueError("k-path coordinate is not in the kpath list")

      return np.reshape(self.kpts[:, kpath_idx], (3,))

   def label_kpt(self, kpt, label, nearest=True):
      self.labels[label] = kpt
