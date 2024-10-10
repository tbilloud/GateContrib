import os
import sys
import matplotlib
import numpy as np
from matplotlib.style.core import library
matplotlib.get_backend()
# matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import uproot
import pandas
import warnings
import awkward as ak
warnings.filterwarnings("ignore", category=DeprecationWarning)
pandas.set_option('display.max_columns', 20), pandas.set_option('display.width', 400)

path = '../output/CC_Coincidences.root'
max_events = -1 # -1 for all

events = uproot.open(os.path.abspath(path) + ':Coincidences')
print(events.num_entries, 'entries in tree Coincidences')
bins = 100

df = events.arrays(['coincID', 'energy', 'layerName'], '(energy>0)', library='pd', entry_stop=max_events)
df_grouped = df.groupby('coincID')
coincSize = df_grouped.size()
for i in range(1, coincSize.max() + 1):
    print('number of coincidences with', i, 'singles:', len(coincSize[coincSize == i]), '(can be in same layer, can be from different events)' if i>1 else '(should be 0?)')

df1 = events.arrays(['coincID', 'energy', 'layerName'], '(energy>0) & (layerName=="scatterer_phys")', library='pd', entry_stop=max_events)
df2 = events.arrays(['coincID', 'energy', 'layerName'], '(energy>0) & (layerName=="absorber_phys")', library='pd', entry_stop=max_events)
e1 = df1['energy']
e2 = df2['energy']

# Plot
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(25, 5))
plot_args = dict(bins=bins, histtype='step', color='blue')
ax1.hist(1000 * e1, range=(0, 1400), **plot_args)
ax1.set_title('first layer', y=-0.15)
ax1.set_xlabel('E1 (keV)', loc='right')
ax1.set_ylabel('Counts')
ax1.set_xlim(xmin=0, xmax=1400)
ax2.hist(1000 * e2, range=(0, 1400), **plot_args)
ax2.set_title('second layer', y=-0.15)
ax2.set_xlabel('E2 (keV)', loc='right')
ax2.set_ylabel('Counts')
ax2.set_xlim(xmin=0, xmax=1400)
# ax3.hist(1000 * esum, range=(0, 2000), **plot_args)
# ax3.set_title('sum', y=-0.15)
# ax3.set_xlabel('E_sum (keV)', loc='right')
# ax3.set_ylabel('Counts')
# ax3.set_xlim(xmin=0, xmax=2000)
plt.tight_layout()
plt.show()
