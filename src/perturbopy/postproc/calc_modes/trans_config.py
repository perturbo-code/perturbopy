import numpy as np

class TransConfig():
    """
    Class representation of a Perturbo imsigma calculation.

    Attributes
    ----------
    temperature : float
        The temperature of this configuration
    chem_potential : float
        The chemical potential of this configuration
    concentration : float
        The carrier concentration of this configuration
    conductivity : np.ndarray
        The 3x3 conductivity tensor of this configuration
    mobility : np.ndarray
        The 3x3 mobility tensor of this configuration
    seebeck_coeff : np.ndarray
        The 3x3 seebeck coefficient tensor of this configuration
    thermal_conductivity : np.ndarray
        The 3x3 thermal conductivity tensor of this configuration
    conductivity_iter : dict
        The dictionary of 3x3 set of conductivity tensors for each of the n_iter iterations of 
        this configuration


    """

    def __init__(self, temperature, chem_potential, concentration, conductivity, mobility, seebeck_coeff, thermal_conductivity, conductivity_iter):
        """
        Constructor method
        
        Attributes
        ----------
        temperature : float
        chem_potential : float
        concentration : float
        conductivity : array_like
        mobility : array_like
        seebeck_coeff : array_like
        thermal_conductivity : array_like
        conductivity_iter : dict

        """

        self.temperature = temperature
        self.chem_potential = chem_potential
        self.concentration = concentration
        self.conductivity = np.array(conductivity)
        self.mobility = np.array(mobility)
        self.seebeck_coeff = np.array(seebeck_coeff)
        self.thermal_conductivity = np.array(thermal_conductivity)

        for iteration in conductivity_iter.keys():
            conductivity_iter[iteration] = np.array(conductivity_iter[iteration])

        self.conductivity_iter = conductivity_iter