import numpy as np


class DynaIndivRun():
    """
    Class representation of a dynamics run

    Attributes
    ----------
    num_steps : int
        Number of time steps

    time_step : float
        Time step in fs

    snap_t : np.ndarray
        Distribution function computed at each time step

    efield : np.ndarray
        Electric field assumed during the calculation. Default value is [0, 0, 0].
    """

    def __init__(self, num_steps, time_step, snap_t, time_units='fs', efield=None):
        """
        Constructor method
        
        Parameters
        ----------
        num_steps : int
        time_step : float
            Time step in fs
        snap_t : array_like

        """

        self.num_steps = num_steps
        self.time_step = time_step
        self.snap_t = snap_t
        self.efield = efield
