import sys

import pandas
import uproot
from pandas import Series

pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 1000)
pandas.set_option('display.float_format', lambda x: f'{x:.1f}')

# Script to print some info about root trees produced by CCMod actor
# ! WARNING! comment out blocks if corresponding tree was not saved
path = '../ideal/output/'
nentries_printed = 1000  # None to read all entries

# ELECTRON ESCAPES
tree = uproot.open(path + 'CC_eventGlobalInfo.root:EventGlobalInfo')
print('\n =>', tree.num_entries, 'entries in tree EventGlobalInfo')
# elec_escape = tree.arrays(library='pd', entry_stop=nentries_printed) # None to read all entries
# print(elec_escape)

# HITS
# stepLength[mm]: distance between two interactions of a particle (e.g.: distance between a gamma particle entering a sensitive volume and being scattered)
# trackLength[mm]: total distance of one particle often including multiple steps. Can also be derived by the trackLocalTime.
# processName: The process by which the particle ended its path in the sensitive detector (e.g.: Transportation (“T”), Optical Absorption(“O”), Comptonscatter(”C”), PhotoElectric(“P”), RaleighScattering(“R”)). You might be interested in distinguishing between particles that are detected at the detector(“T”) and those that were absorbed(“O”). A particle that undergoes Comptonscatter(“C”) is counted as two hits when it splits up.
tree = uproot.open(path + 'CC_Hits.root:Hits')
print('\n =>', tree.num_entries, 'entries in tree Hits')
hits = tree.arrays(library='pd', entry_stop=nentries_printed)  # None to read all entries
columns_to_remove = ['runID', 'time', 'sourcePDG', 'sourceEnergy', 'sourcePosX', 'sourcePosY', 'sourcePosZ', 'volumeID']
columns_to_remove += ['posX', 'posY', 'posZ', 'localPosX', 'localPosY', 'localPosZ']
columns_to_remove += ['nCrystalConv', 'nCrystalCompt', 'nCrystalRayl']
hits = hits.drop(columns=columns_to_remove)
hits['edep'] = round(hits['edep'] * 1000, 2)  # convert to keV
hits['energyIniT'] = round(hits['energyIniT'] * 1000, 2)  # convert to keV
hits['energyFinal'] = round(hits['energyFinal'] * 1000, 2)  # convert to keV
hits['stepLength'] = round(hits['stepLength'] * 1000, 2)  # convert to um
hits['trackLength'] = round(hits['trackLength'] * 1000, 2)  # convert to um
hits['trackLocalTime'] = round(hits['trackLocalTime'] * 1e15, 2)  # convert to fs
hits = hits[hits['eventID'].isin([11,33])]
print(hits.to_string(index=False))
# print(Series(hits['postStepProcess'].to_numpy()).value_counts(normalize=True) * 100,'\n')  # !! entry_stop = None  !!

# SINGLES
tree = uproot.open(path + 'CC_Singles.root:Singles')
print('\n =>', tree.num_entries, 'entries in tree Singles')
singles = tree.arrays(library='pd', entry_stop=nentries_printed)
print(singles)

# COINCIDENCES
tree = uproot.open(path + 'CC_Coincidences.root:Coincidences')
print('\n =>', tree.num_entries, 'entries in tree Coincidences')
coincidences = tree.arrays(library='pd', entry_stop=nentries_printed)
print(coincidences)

# COINCIDENCES SEQUENCES
tree = uproot.open(path + 'CC_sequenceCoincidence.root:sequenceCoincidence')
print('\n =>', tree.num_entries, 'entries in tree sequenceCoincidence')
seqCoin = tree.arrays(library='pd', entry_stop=nentries_printed)
print(len(seqCoin[seqCoin['nCrystalRayl'] > 0]), 'entries with nCrystalRayl > 0')  # !! entry_stop = None  !!
# print(seqCoin)
# print(seqCoin[seqCoin['coincID'] == 48])
# print(seqCoin[seqCoin['nCrystalRayl'] > 0])

# # CONES => comment out if cone tree was not created (has to be done after simulation)
# tree = uproot.open(path + 'CC_Cones.root:Cones')
# print('\n =>',tree.num_entries, 'entries in tree Cones')
# cones = tree.arrays(library='pd', entry_stop=nentries_printed)
# print(cones)
# print(Series(cones['nSingles'].to_numpy()).value_counts(normalize=True) * 100) # !! entry_stop = None for that !!

# # To use with nentries_printed = None
# eventId = 96212
# print(hits[hits['eventID'] == eventId])
# print(singles[singles['eventID'] == eventId])
# print(coincidences[coincidences['eventID'] == eventId])
# print(seqCoin[seqCoin['eventID'] == eventId])
