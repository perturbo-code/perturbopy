import numpy as np

"""
This is a module for performing calculations related to a
crystal lattice

"""


def reshape_kpts(kpts):
   """
   Method to reshape k-points into a 2d array of shape (3, N)
   such that k-points are column-oriented
      - a list of k-points will be transformed to an array
      - an array of k-points with shape (N, 3) will be reshaped
        to shape (N, 3) if N != 3
      - Note that k-points with shape (3, 3) will be assumed to
        have the correct shape
f
   Parameters
   ----------
   kpts: array
      An array or list of k-points with shape (3,N), (N,3), or (3,)
   
   Returns
   -------
   kpts: array
      An array of k-points with shape (3,N)

   """
   kpts = np.array(kpts)

   if np.shape(kpts)[0] == 3:
      if len(np.shape(kpts)) == 1:
         return np.reshape(kpts, (3, 1))
      else:
         return kpts
   elif np.shape(kpts)[1] != 3:
      raise ValueError('K-point vectors should be inputted as a 3xN matrix, where N is the number of vectors.')
   else:
      return np.transpose(kpts)


def cryst_to_cart(vectors, lat, recip_lat, forward=True, real_space=True):
   """
   Method to convert atomic coordinates and k-point coordinates
   between crystal and cartesian coordinates, given the crystal
   lattice. Real space points in cartesian units have units of alat.
   Reciprocal points in cartesian coordinates have units of 2pi/a.

   Parameters
   ----------
   vectors : array
      3xN Array of vectors [v1, v2, v3 ...] to be converted

   lat : array
      3x3 array of lattice vectors [v1, v2, v3] in units of alat

   recip_lat : array
      3x3 array of reciprocal lattice vectors [v1, v2, v3 in units of
      2pi/a

   forward : bool
      If true, vectors will be converted from crystal to cartesian
      coordinates. If false, vectors will be converted from
      cartesian to crystal coordinates

   real_space : bool
      If true, vectors are assumed to be in real space
      (i.e. atomic positions). If false, vectors are assumed to
      be in reciprocal space (i.e. k-points)

   Returns
   -------
   converted_vectors : array
      Array containing the converted vectors [v1, v2, v3, ...]

   """

   if np.shape(vectors)[0] != 3:
      raise ValueError('Vectors should be inputted as a 3xN matrix, where N is the number of vectors.')

   if forward:
      if real_space:
         conversion_mat = lat
      else:
         conversion_mat = recip_lat
  
   else:
      if real_space:
         conversion_mat = np.transpose(recip_lat)
      else:
         conversion_mat = np.transpose(lat)

   converted_vectors = np.tensordot(conversion_mat, vectors, axes=1)

   return converted_vectors
