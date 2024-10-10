import os
import matplotlib
import numpy as np
matplotlib.get_backend()
import matplotlib.pyplot as plt
import uproot

path = '../output/CC_Singles.root'
bins = 100

pSingles = uproot.open(os.path.abspath(path) + ':Singles')
print(pSingles.num_entries, 'singles')
energy_scatterer = 1000 * pSingles.arrays(['energy'], '(energy>0) & (layerName=="scatterer_phys")')['energy']
energy_absorber = 1000 *  pSingles.arrays(['energy'], '(energy>0) & (layerName=="absorber_phys")')['energy']
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5))
plot_args = dict(bins=bins, range=(0, 1500), histtype='step', color='blue')
ax1.hist(np.array(energy_scatterer), **plot_args)
ax1.set_title('Scatterer')
ax1.set_xlabel('E1 (keV)', loc='right')
ax1.set_ylabel('Counts')
ax1.set_xlim(xmin=0)
ax2.hist(energy_absorber, **plot_args)
ax2.set_title('Absorber')
ax2.set_xlabel('E2 (keV)', loc='right')
ax2.set_ylabel('Counts')
ax2.set_xlim(xmin=0)
plt.tight_layout()
plt.show()
