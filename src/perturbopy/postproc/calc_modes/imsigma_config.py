import numpy as np


class ImsigmaConfig():
    """
    Class representation of a Perturbo imsigma calculation.

    Attributes
    ----------
    temperature : float
        The temperature of this configuration
    chem_potential : float
        The chemical potential of this configuration
    imsigma : dict
        Dictionary of arrays, where keys represent the band index, and arrays are Im(Sigma) values
        for each k-point at that band index
    imsigma_mode : dict
        Dictionary of imsigma dictionaries, where the keys represent phonon modes (numbered by increasing phonon energy).
        Each dict gives the Im(Sigma) values by band for each k-point due to that phonon mode.

    """

    def __init__(self, temperature, chem_potential, imsigma, imsigma_mode):
        """
        Constructor method
        
        Attributes
        ----------
        temperature : float
        chem_potential : float
        imsigma : dict
        imsigma_mode : dict

        """

        self.temperature = temperature
        self.chem_potential = chem_potential

        for band_idx in imsigma.keys():
            imsigma[band_idx] = np.array(imsigma[band_idx])

            for mode in imsigma_mode[band_idx].keys():
                imsigma_mode[band_idx][mode] = np.array(imsigma_mode[band_idx][mode])

        self.imsigma = imsigma
        self.imsigma_mode = imsigma_mode
