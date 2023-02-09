import numpy as np
from perturbopy.postproc.utils.constants import standardize_units_name, recip_points_units_names, special_recip_points
from perturbopy.postproc.utils.lattice import cryst_to_cart, reshape_points
from perturbopy.postproc.utils import lattice


class RecipPtDB():
   """
   This is a class representation of a set of points in reciprocal space.

   Parameters
   ----------
   points_cart : array_like
      Array of reciprocal space points in cartesian coordinates, in units of 2pi/a.

   points_cryst : array_like
      Array of reciprocal space points in crystal coordinates.

   _units : str
      The units that calculations will be performed in (crystal or cartesian).
      If _units = 'crystal', then points_cryst will be used instead of points_cart when
      a method such as "distances" is called on the RecipPtDB object.

   path : array_like
      Array of numbers corresponding to each reciprocal space point, for plotting purposes.

   path_units : str
      Units of path, typically arbitrary

   labels : dict
      Dictionary of reciprocal space point labels
      example: {"Gamma": [0, 0, 0], 'L': [.5,.5,.5]}

   """

   def __init__(self, points_cart, points_cryst, units='crystal', path=None, path_units='arbitrary', labels={}):

      """
      Constructor method

      """
      self.points_cart = reshape_points(points_cart)
      self.points_cryst = reshape_points(points_cryst)
      self._units = standardize_units_name(units, recip_points_units_names)

      if path is None:
         self.path = np.arange(0, np.shape(self.points_cart)[1])
      else:
         self.path = path

      self.path_units = path_units

      if labels == {}:
         labels = special_recip_points

      self.labels = labels

   @classmethod
   def from_lattice(self, points, units, lat, recip_lat, path=None, path_units='arbitrary', labels={}):
      """
      Class method to create a RecipPtDB from one set of reciprocal space points and the lattice information.

      Parameters
      ----------
      points : array
         Array of reciprocal space points in cartesian or crystal coordinates

      units : str
         The units points are given in

      lat : array
         3x3 array of lattice vectors [v1, v2, v3] in units of alat

      recip_lat : array
         3x3 array of reciprocal lattice vectors [v1, v2, v3] in units of
         2pi/a

      path : array, optional
         Array of values corresponding to each reciprocal space point, for plotting purposes

      path_units : str, optional
         Units of the path points, typically arbitrary

      labels : dict, optional
         Dictionary of reciprocal space point labels
         example: {"Gamma": [0, 0, 0], 'L': [.5,.5,.5]}

      Returns
      -------
      points_db : RecipPtDB
         The RecipPtDB created from the lattice information and reciprocal space points
      """
      units = standardize_units_name(units, recip_points_units_names)
      
      if units == 'cartesian':
         points_cart = reshape_points(points)
         points_cryst = cryst_to_cart(points_cart, lat, recip_lat, forward=False, real_space=False)

      elif units == 'crystal':

         points_cryst = reshape_points(points)
         points_cart = cryst_to_cart(points_cryst, lat, recip_lat, forward=True, real_space=False)
      else:
         return None

      return RecipPtDB(points_cart, points_cryst, units, path, path_units, labels)

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
         The new reciprocal point units, which will be assumed in future calculations
         on the RecipPtDB object

      """
      print(f"Converting units to {new_units}")
      self._units = standardize_units_name(new_units, recip_points_units_names)

   
   @property
   def points(self):
      """
      Property storing the reciprocal space points corresponding to the units property.
      i.e. if self.units = "crystal", then points_cryst will be returned.
      If self.units = "cartesian", then points_cart will be returned.

      Returns
      -------
      points : array
         the reciprocal space points corresponding the units property

      """

      if self.units == 'cartesian':
         return self.points_cart
      elif self.units == 'crystal':
         return self.points_cryst

   def scale_path(self, range_min, range_max):
      """
      Method to scale the arbitrary k path plotting coordinates to a certain range.

      Parameters
      ----------
      range_min : float
         Lower limit of the range to which the k path coordinates will be scaled.

      range_max : float
         Upper limit of the range to which the k path coordinates will be scaled.

      Returns
      -------
      None

      """

      self.path = (self.path - min(self.path)) \
                               / (max(self.path) - min(self.path)) \
                               * (range_max - range_min) \
                               + range_min

   def distances(self, point):
      """
      Method to compute the distances between each reciprocal space point in the points property
      and an inputted reciprocal space point

      Parameters
      ----------
      point : array
         The reciprocal space point that distances will be computed from

      Returns
      -------
      distances : array
         an array of distances between each reciprocal space point in the points property and point

      """
      distances = lattice.compute_distances(self.points, point)
      
      return distances

   def where(self, point,**kwargs):
      """
      Method to find the index or indices of a particular point

      Parameters
      ----------
      point : array
         The reciprocal space point to be searched
      **kwargs : dict
         Extra arguments for point_to_path method. Refer to Lattice module documentation for a list of all possible arguments.

      Returns
      -------
      points_indices : list
         The indices of the matching reciprocal space point in the points array
      
      """
      points_indices = lattice.where(point, self.points, **kwargs)

      return points_indices

   def point_to_path(self, point, **kwargs):
      """
      Method to find the path coordinate corresponding to a reciprocal space point coordinate

      Parameters
      ----------
      point : list
         The reciprocal space point to be searched

      nearest : bool
         If true, the path coordinate of the reciprocal space point closest to the point input will
         be returned if the inputted point is not found
      **kwargs : dict
         Extra arguments for point_to_path method. Refer to Lattice module documentation for a list of all possible arguments.

      Returns
      -------
      path_coord : array
         The path coordinates of the corresponding reciprocal space point(s)

      """

      path_coord = self.path[self.where(point, nearest)]

      return path_coord

   def path_to_point(self, path, nearest=True, **kwargs):
      """
      Method to find the reciprocal space point corresponding to a path coordinate

      Parameters
      ----------
      point : list
         The reciprocal point to be searched

      nearest : bool
         If true, the point of the closest path coordinate will be returned if the inputted path
         coordinate is not found

      Returns
      -------
      coord_path : list
         The reciprocal space point(s) of the corresponding path coordinate

      """
      atol = kwargs.pop('atol', 1e-16)
      rtol = kwargs.pop('atol', 1e-10)

      if path in self.path:
         path_idx = np.isclose(self.path, path)
      else:
         if nearest:
            distances = np.abs(self.path - path)
            min_distance = np.amin(distances)
            path_idx = np.where(np.isclose(distances, min_distance, atol=atol, rtol=rtol))[0]
         else:
            raise ValueError("path coordinate is not in the path list")

      return np.reshape(self.points[:, path_idx], (3,))

   def add_labels(self, labels_dict_input, **kwargs):
      """
      Method to add a label associated with a reciprocal space point. For example, point = [0,0,0] and label = 'gamma'

      Parameters
      ----------
      points : list
         A list of reciprocal space points

      labels : str
         The labels associated with the inputted reciprocal space points, in order

      nearest : bool
         If true, the reciprocal space point closest to the inputted point will be labeled if the inputted point is
         not found

      """

      for i, label in enumerate(labels_dict_input.keys()):
         self.labels[label] = labels_dict_input[label] 

   def remove_labels(self, labels_list, **kwargs):

      for i, label in labels_list:
         self.labels = self.labels.pop(label)
