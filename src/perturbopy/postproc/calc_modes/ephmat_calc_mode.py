class EphmatCalcMode(CalcMode):
    """
    Class representation of a Perturbo ephmat calculation.

    Parameters
    ----------
    pert_dict : dict
    Dictionary containing the inputs and outputs from the ephmat calculation.

    Attributes
    ----------


    """

    def __init__(self, pert_dict):
        """
        Constructor method

        """
        super().__init__(pert_dict)

        if self.calc_mode != 'ephmat':
            raise ValueError('Calculation mode for a ephmatCalcMode object should be "ephmat"')

        phdisp_units = self._pert_dict['ephmat'].pop('phonon energy units')
        defpot_units = self._pert_dict['ephmat'].pop('deformation potential units')
        ephmat_units = self._pert_dict['ephmat'].pop('e-ph matrix elements units')
        nmode = self._pert_dict['ephmat'].pop('number of phonon modes')

        kpath_units = self._pert_dict['ephmat'].pop('k-path coordinate units')
        kpath = np.array(self._pert_dict['ephmat'].pop('k-path coordinates'))
        kpoint_units = self._pert_dict['ephmat'].pop('k-point coordinate units')
        kpoint = np.array(self._pert_dict['ephmat'].pop('k-point coordinates'))
        
        qpath_units = self._pert_dict['ephmat'].pop('q-path coordinate units')
        qpath = np.array(self._pert_dict['ephmat'].pop('q-path coordinates'))
        qpoint_units = self._pert_dict['ephmat'].pop('q-point coordinate units')
        qpoint = np.array(self._pert_dict['ephmat'].pop('q-point coordinates'))

        ephmat_dat = self._pert_dict['ephmat'].pop('phonon index')
        
        self.kpt = RecipPtDB.from_lattice(kpoint, kpoint_units, self.lat, self.recip_lat, kpath, kpath_units)
        self.qpt = RecipPtDB.from_lattice(qpoint, qpoint_units, self.lat, self.recip_lat, qpath, qpath_units)

        phdisp = {}
        defpot = {}
        ephmat = {}

        for phidx in ephmat_dat.keys():
            phdisp[phidx] = ephmat_dat[phidx].pop('phonon energy')
            defpot[phidx] = ephmat_dat[phidx].pop('deformation potential')
            ephmat[phidx] = ephmat_dat[phidx].pop('e-ph matrix elements')

        self.phdisp = EnergyDB(phdisp, phdisp_units)
        self.defpot = EnergyDB(defpot, defpot_units)
        self.ephmat = EnergyDB(ephmat, ephmat_units)

    def plot_phdisp

    def plot_defpot

    def plot_ephmat

    def compare_ephmat



        