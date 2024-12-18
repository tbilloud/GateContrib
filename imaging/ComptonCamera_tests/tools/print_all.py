import sys
import uproot
from pandas import Series
import pandas
pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 1000)
pandas.set_option('display.float_format', lambda x: f'{x:.5f}')

# Script to print some info about root trees produced by CCMod actor
# ! WARNING! comment out blocks if corresponding tree was not saved
path = '../ideal/output/'

# ELECTRON ESCAPES
tree = uproot.open(path + 'CC_eventGlobalInfo.root:EventGlobalInfo')
print('\n =>', tree.num_entries, 'entries in tree EventGlobalInfo')
# elec_escape = tree.arrays(library='pd', entry_stop=None) # None to read all entries
# elec_escape = elec_escape.drop(columns=['runID'])
# print(elec_escape.to_string(index=False))

# HITS
# stepLength[mm]: distance between two interactions of a particle (e.g.: distance between a gamma particle entering a sensitive volume and being scattered)
# trackLength[mm]: total distance of one particle often including multiple steps. Can also be derived by the trackLocalTime.
# processName: The process by which the particle ended its path in the sensitive detector (e.g.: Transportation (“T”), Optical Absorption(“O”), Comptonscatter(”C”), PhotoElectric(“P”), RaleighScattering(“R”)). You might be interested in distinguishing between particles that are detected at the detector(“T”) and those that were absorbed(“O”). A particle that undergoes Comptonscatter(“C”) is counted as two hits when it splits up.
# WARNING: A particle that undergoes Comptonscatter(“C”) is counted as two hits when it splits up.
tree = uproot.open(path + 'CC_Hits.root:Hits')
print('\n =>', tree.num_entries, 'entries in tree Hits')
hits = tree.arrays(library='pd', entry_stop=200)  # None to read all entries
columns_to_remove = ['runID', 'time', 'sourcePDG', 'sourceEnergy', 'sourcePosX', 'sourcePosY', 'sourcePosZ', 'volumeID']
columns_to_remove += ['posX', 'posY', 'posZ', 'localPosX', 'localPosY', 'localPosZ']
columns_to_remove += ['nCrystalConv', 'nCrystalCompt', 'nCrystalRayl']
columns_to_remove += ['trackLocalTime','stepLength','trackLength']
hits = hits.drop(columns=columns_to_remove)
hits['edep'] = hits['edep'] * 1000  # convert to keV
hits['energyIniT'] = hits['energyIniT'] * 1000  # convert to keV
hits['energyFinal'] = hits['energyFinal'] * 1000  # convert to keV
# print(Series(hits['postStepProcess'].to_numpy()).value_counts(normalize=True) * 100,'\n')  # !! entry_stop = None  !!
# print(Series(hits['layerName'].to_numpy()).value_counts(normalize=True) * 100,'\n')  # !! entry_stop = None  !!
# print(hits.groupby('eventID')['edep'].sum())
# hits = hits[hits['eventID'].isin([751,2027,2703])]
#print(hits[hits['postStepProcess'] == 'compt'])
#print(hits.to_string(index=False))

# SINGLES
tree = uproot.open(path + 'CC_Singles.root:Singles')
print('\n =>', tree.num_entries, 'entries in tree Singles')
singles = tree.arrays(library='pd', entry_stop=10)
columns_to_remove = ['runID', 'time', 'sourcePDG', 'sourceEnergy', 'sourcePosX', 'sourcePosY', 'sourcePosZ', 'volumeID']
columns_to_remove += ['localPosX', 'localPosY', 'localPosZ']
columns_to_remove += ['nCrystalConv', 'nCrystalCompt', 'nCrystalRayl']
singles = singles.drop(columns=columns_to_remove)
singles['energy'] = singles['energy'] * 1000 # convert to keV
singles['energyIni'] = singles['energyIni'] * 1000  # convert to keV
singles['energyFinal'] = singles['energyFinal'] * 1000  # convert to keV
sgroup = singles.groupby("eventID").size()
print('\n'.join([f'number of events with {i} singles: {len(sgroup[sgroup == i])}' for i in range(1, sgroup.max() + 1)]))
# print(singles[singles['eventID'].isin(singles.groupby('eventID').filter(lambda x: len(x) == 3)['eventID'].unique())])
# print(singles[singles['eventID'].isin([11,33])])
# print(Series(singles['layerName'].to_numpy()).value_counts(normalize=True) * 100,'\n')  # !! entry_stop = None  !!
# print(singles.to_string(index=False))
# sys.exit()

# SINGLE + HITS SIDE BY SIDE
dfc = pandas.concat([hits, singles.add_prefix('_')], axis=1)
print('\n =>', len(dfc), 'entries in dataframe Singles + Hits')
dfc['_eventID'] = dfc['_eventID'].fillna(-1).astype(int)
print(dfc[dfc['eventID'].isin([0])].to_string(index=False))
edep_sum = hits[hits['eventID'].isin([0])].groupby('trackID')['edep'].sum().reset_index()
print(edep_sum)
sys.exit()

# COINCIDENCES
tree = uproot.open(path + 'CC_Coincidences.root:Coincidences')
print('\n =>', tree.num_entries, 'entries in tree Coincidences')
# coincidences = tree.arrays(library='pd', entry_stop=1)
# print(coincidences)

# COINCIDENCES SEQUENCES
tree = uproot.open(path + 'CC_sequenceCoincidence.root:sequenceCoincidence')
print('\n =>', tree.num_entries, 'entries in tree sequenceCoincidence')
# seqCoin = tree.arrays(library='pd', entry_stop=1)
# print(len(seqCoin[seqCoin['nCrystalRayl'] > 0]), 'entries with nCrystalRayl > 0')  # !! entry_stop = None  !!
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
