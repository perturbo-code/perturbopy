import perturbopy.postproc as ppy
import os
import matplotlib.pyplot as plt

base = "C:\\Users\\shael\\github\\perturbopy\\tests"
si_ephmat = ppy.EphmatCalcMode.from_yaml(os.path.join(base, "refs", "si_ephmat.yml"))
fig, ax = plt.subplots()
si_ephmat.plot_ephmat(ax)
plt.show()