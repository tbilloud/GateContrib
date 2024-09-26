import os
import matplotlib
matplotlib.get_backend()
#matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import uproot


path='../output/CC_clustering_Singles.root'
pSingles = uproot.open(os.path.abspath(path) + ':Singles')
print(pSingles.num_entries,'entries')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
plot_args = dict(bins=100, range=(0,1500), histtype='step', color='red')
ax1.hist(1000*pSingles.arrays(['energy'], 'layerName=="scatterer_phys"')['energy'], **plot_args)
ax1.set_title('Scatterer')
ax1.set_xlabel('E1 (keV)')
ax1.set_ylabel('Counts')
ax2.hist(1000*pSingles.arrays(['energy'],'layerName=="absorber_phys"')['energy'], **plot_args)
ax2.set_title('Absorber')
ax2.set_xlabel('E2 (keV)')
ax2.set_ylabel('Counts')
plt.tight_layout()
plt.show()
