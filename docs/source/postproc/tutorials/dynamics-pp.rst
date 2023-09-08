Dynamics-run tutorial
=====================

In this section, we describe how to use Perturbopy to process a Perturbo ``dynamics-pp`` calculation.

The ultrafast dynamics calculation solves the real-time Boltzman transport equation (rt-BTE). Please see the `Perturbo website <https://perturbo-code.github.io/mmydoc_dynamics.html>`_ for more details. We first run the Perturbo calculation following the instructions on the Perturbo website and obtain the YAML file, *si_dynamics-pp.yml*. We also obtain the popu HDF5 file *si_popu.h5*, which stores results from the ``dynamics-pp`` calculation too lage to be outputted to the YAML file.

popu_path = "si_popu.h5"
yaml_path = "si_dynamics_pp.yml"

si_dyna_pp = ppy.DynamicsPPCalcMode.from_hdf5_yaml(popu_path, yaml_path)
fig, ax = plt.subplots()

snap_number=25

plt.plot(si_dyna_pp.energy_grid,si_dyna_pp.popu[:, snap_number],marker='o',linestyle='', markersize=2.5)

plt.xlabel('Energy (eV)', fontsize = 20)
plt.ylabel('Electron population', fontsize = 20)
plt.xticks(fontsize= 18)
plt.yticks(fontsize= 18)
plt.show()