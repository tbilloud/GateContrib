import pandas
import uproot

pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 1000)

# Script to print some info about root trees produced by CCMod actor
# ! WARNING! comment out blocks if corresponding tree was not saved
path = '/home/billoud/PycharmProjects/GateContrib/imaging/ComptonCamera_tests/ideal/sourcePoint_cameraSingle/output/'
#path = '/media/billoud/Volume/CT/GATE/ideal/time1_camera_posX0_posY0/'
nentries_printed = None # None to read all entries

# Info about electron escape
tree = uproot.open(path + 'CC_eventGlobalInfo.root:EventGlobalInfo')
print(tree.num_entries, 'entries in tree EventGlobalInfo')
# df = tree.arrays(library='pd')
# print(df)

# Info about 'hits'
tree = uproot.open(path + 'CC_Hits.root:Hits')
print(tree.num_entries, 'entries in tree Hits')
hits = tree.arrays(library='pd', entry_stop=nentries_printed)
# print(hits)
# print(hits[hits['postStepProcess'] == 'Rayl'])

# Info about 'singles'
tree = uproot.open(path + 'CC_Singles.root:Singles')
print(tree.num_entries, 'entries in tree Singles')
singles = tree.arrays(library='pd', entry_stop=nentries_printed)
# print(df)

# PrintInfo about 'coincidences'
tree = uproot.open(path + 'CC_Coincidences.root:Coincidences')
print(tree.num_entries, 'entries in tree Coincidences')
coincidences = tree.arrays(library='pd', entry_stop=nentries_printed)
# print(coincidences)

# PrintInfo about 'coincidence sequences'
tree = uproot.open(path + 'CC_sequenceCoincidence.root:sequenceCoincidence')
print(tree.num_entries, 'entries in tree sequenceCoincidence')
seqCoin = tree.arrays(library='pd', entry_stop=nentries_printed)
#print(seqCoin[:50])
print(seqCoin[seqCoin['coincID'] == 48])

# # PrintInfo about 'cones' => comment out if cone tree was not created (has to be done after simulation)
# tree = uproot.open(path + 'CC_Cones.root:Cones')
# print(tree.num_entries, 'entries in tree Cones')
# cones = tree.arrays(library='pd', entry_stop=nentries_printed)
# print(cones)
# # Set entry_stop to -1 if using the following
# print(len(cones[cones['nSingles'] == 1]),'entries with nSingles == 1')
# print(len(cones[cones['nSingles'] == 2]),'entries with nSingles == 2')
# print(len(cones[cones['nSingles'] == 3]),'entries with nSingles == 3')

# To use with nentries_printed = None
eventId = 96212
print(hits[hits['eventID'] == eventId])
print(singles[singles['eventID'] == eventId])
print(coincidences[coincidences['eventID'] == eventId])
print(seqCoin[seqCoin['eventID'] == eventId])