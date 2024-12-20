import os
import matplotlib
import numpy as np
from IPython.core.pylabtools import figsize

matplotlib.get_backend()
import matplotlib.pyplot as plt
import uproot
from pathlib import Path

path = Path('../Gate9.2/output')
#path = '../output/source_x30mm_time20/CC_Singles.root'
emax_keV = 150

singles = uproot.open(str(path / 'CC_Singles.root') + ':Singles')
print(singles.num_entries, 'entries in tree Singles')
single_energies = 1000 * singles.arrays(['energy'], '(layerName=="absorber_phys")')['energy']
print(len(single_energies[single_energies < 0]), 'singles with negative energy')

# plt.figure(figsize=(20,10))
# plot_args = dict(bins=emax_keV, range=(0, emax_keV), histtype='step', color='blue', linestyle='dotted')
# plt.hist(np.array(energies), **plot_args)
# plt.xlabel('E1 (keV)', loc='right')
# plt.ylabel('Counts')
# plt.xlim(xmin=0)
# plt.tight_layout()
# plt.show()

seqCoin = uproot.open(str(path / 'CC_sequenceCoincidence.root') + ':sequenceCoincidence')
print(seqCoin.num_entries, 'entries in tree sequenceCoincidence')
df = seqCoin.arrays(['coincID', 'eventID','energy'], '(layerName=="absorber_phys")', library='pd')
#df = df.groupby('coincID').filter(lambda x: len(x) == 2).groupby('coincID').sum()
print('\n'.join([f'number of coincidences with {i} singles: {len(df.groupby("coincID").size()[df.groupby("coincID").size() == i])}{" (from different events/decays)" if i > 2 else ""}' for i in range(2, df.groupby("coincID").size().max() + 1)]))
df_sum = df.drop(columns='eventID').groupby('coincID').sum()
print(df[:20],2*'\n',df_sum[:10])
seqCoin_energies = 1000 * df_sum['energy']

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 10))
plot_args = dict(bins=emax_keV, range=(0, emax_keV))
ax1.hist(np.array(single_energies), **plot_args)
ax1.set_title('Singles / clusters')
ax1.set_xlabel('E (keV)', loc='right')
ax1.set_ylabel('Counts')
ax1.set_xlim(xmin=0)
ax2.set_title('Sum of coincident singles / clusters')
ax2.hist(np.array(seqCoin_energies), **plot_args)
ax2.set_xlabel('E (keV)', loc='right')
ax2.set_ylabel('Counts')
ax2.set_xlim(xmin=0)
fig.tight_layout()
fig.show()
