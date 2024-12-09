import sys

import matplotlib.pyplot as plt
import pandas as pd
import uproot
import numpy as np

pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 400)
pd.set_option('display.max_rows', 1000)

# Script to plot doppler broadening
# Faster than using hits tree

path = '/imaging/ComptonCamera_tests/ideal/output/'
nentries_printed = 10 # None to read all entries

tree = uproot.open(path + 'CC_sequenceCoincidence.root:sequenceCoincidence')
print(tree.num_entries, 'entries in tree sequenceCoincidence, keeping', nentries_printed)

# TODO grouping is extremely slow
# TODO dont group, keep all entries and just keep after 2nd event in sequence
# df = tree.arrays(library='pd', entry_stop=nentries_printed)
# # print(df)
#
# # keep only entries belonging to a group of exactly 2 with same eventID and one has postStepProcess == 'compt' and the other has postStepProcess == 'phot', knowing that postStepProcess can also be Rayl
# df = df.groupby('eventID').filter(lambda x: len(x) == 2)
# print(len(df),'grouped')
#
# def calculate_angle(row):
#     posX, posY, posZ = 'globalPosX', 'globalPosY', 'globalPosZ'
#     vector1 = np.array([row.iloc[0][posX], row.iloc[0][posY], row.iloc[0][posZ]])
#     vector2 = np.array([row.iloc[1][posX], row.iloc[1][posY], row.iloc[1][posZ]])
#     dot_product = np.dot(vector1, vector2)
#     norm1 = np.linalg.norm(vector1)
#     norm2 = np.linalg.norm(vector2)
#     angle = np.arccos(dot_product / (norm1 * norm2))
#     return np.degrees(angle)
#
# # Group by eventID and calculate the angle for each group
# result = df.groupby('eventID').apply(lambda x: pd.Series({
#     'eventID': x['eventID'].iloc[0],
#     'angle': calculate_angle(x),
#     'energy': x['energy'].iloc[0]
# })).reset_index(drop=True)
# result['eventID'] = result['eventID'].astype(int)
#
# print(len(result),'good events')
# # print(result)
#
# # plot histograms of angles and energies side by side
# fig, axs = plt.subplots(1, 2, figsize=(10, 5))
# axs[0].hist(result['angle'], bins=100) #, range=(0, 180))
# axs[0].set_title('Angles')
# axs[0].set_xlabel('Angle (degrees)')
# axs[0].set_ylabel('Counts')
# axs[1].hist(1000*result['energy'], bins=100) #, range=(0, 1000)
# axs[1].set_title('Energies')
# axs[1].set_xlabel('Energy (keV)')
# axs[1].set_ylabel('Counts')
# plt.show()

# TODO this might be faster than using dataframes
# for batch in tree.iterate(step_size=1, entry_stop=nentries_printed):
#     print(batch)