import os
import numpy as np
from perturbopy.io_utils.io import open_yaml


class CalcMode():
    """
    This is a general class representation of a Perturbo calculation mode.

    Parameters
    ----------
    _pert_dict : dict
       dictionary containing inputs and outputs from a Perturbo calculation, as well as
       basic data of the material. Typically obtained from the YAML file outputted by Perturbo.
    alat : float
    alat_units : str
    lat : array
    lat_units : str
    recip_lat : array
    recip_lat_units : str
    nat : int
    atomic_pos : array
    atomic_pos_units : str
    volume : float
    volume_units : str
    nsym : int
    kc_dim : array
    polar_alpha : float
    epsil : array
    qc_dim : array
    mass : array
    mass_units : str
    symop : array
    zstart : array
    system_2d : bool
    num_wann : int
    wannier_center : array
    wannier_center_cryst : array

    """

    def __init__(self, pert_dict):
        """
        Constructor method

        """

        # Extract calculation mode name and prefix from pert_dict
        self.calc_mode = pert_dict['input parameters']['after conversion'].pop('calc_mode')
        self.prefix = pert_dict['input parameters']['after conversion'].pop('prefix')

        # Extract basic data from pert_dict
        self.alat = pert_dict['basic data']['alat']
        self.alat_units = pert_dict['basic data']['alat units']
        self.lat = np.transpose(np.array(pert_dict['basic data']['lattice vectors']))
        self.lat_units = pert_dict['basic data']['lattice vectors units']
        self.recip_lat = np.transpose(np.array(pert_dict['basic data']['reciprocal lattice vectors']))
        self.recip_lat_units = pert_dict['basic data']['reciprocal lattice vectors units']
        self.nat = pert_dict['basic data']['number of atoms in unit cell']
        self.atomic_pos = np.transpose(np.array(pert_dict['basic data']['atomic positions']))
        self.atomic_pos_units = pert_dict['basic data']['atomic positions units']
        self.volume = pert_dict['basic data']['volume']
        self.volume_units = pert_dict['basic data']['volume units']
        self.nsym = pert_dict['basic data']['number of symmetry operations']
        self.kc_dim = np.array(pert_dict['basic data']['kc dimensions'])
        self.polar_alpha = pert_dict['basic data']['polar_alpha']
        self.epsil = np.transpose(np.array(pert_dict['basic data']['epsil']))
        self.qc_dim = np.array(pert_dict['basic data']['qc dimensions'])
        self.mass = np.array(pert_dict['basic data']['mass'])
        self.mass_units = pert_dict['basic data']['mass units']
        self.symop = [pert_dict['basic data']['symop']]
        self.zstar = [pert_dict['basic data']['zstar']]
        self.system_2d = pert_dict['basic data']['system_2d']
        self.num_wann = pert_dict['basic data']['number of Wannier functions']
        self.wannier_center = np.transpose(np.array(pert_dict['basic data']['wannier_center']))
        self.wannier_center_cryst = np.transpose(np.array(pert_dict['basic data']['wannier_center_cryst']))

        # Store remaining, unprocessed data from pert_dict (often, such data is calculation mode specific)
        self._pert_dict = pert_dict

    @classmethod
    def from_yaml(cls, yaml_path='pert_output.yml'):
        """
        Class method to create a CalcMode object from the YAML file
        generated by a Perturbo calculation.

        Parameters
        ----------
        yaml_path : str, optional
           Path to the YAML file generated by a Perturbo calculation

        Returns
        -------
        calc_mode : CalcMode
           The CalcMode object generated from the YAML file

        """

        if not os.path.isfile(yaml_path):
            raise FileNotFoundError(f'File {yaml_path} not found')

        yaml_dict = open_yaml(yaml_path)

        return cls(yaml_dict)
