import pandas
import uproot

pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 1000)

# Script to print some info about root trees produced by CCMod actor
# ! WARNING! comment out blocks if corresponding tree was not saved
path = '../output/'
nentries_printed = 3

# Info about electron escape
# tree = uproot.open(path + 'CC_eventGlobalInfo.root:EventGlobalInfo')
# print(tree.num_entries, 'entries in tree Hits')
# df = tree.arrays(library='pd')
# print(df[:nevent_printed])

# Info about 'hits'
# tree = uproot.open(path + 'CC_Hits.root:Hits')
# print(tree.num_entries, 'entries in tree Hits')
# df = tree.arrays(library='pd')
# print(df[df['eventID'] == 7043])
# # print(df[:nevent_printed])

# Info about 'singles'
tree = uproot.open(path + 'CC_Singles.root:Singles')
print(tree.num_entries, 'entries in tree Singles')
df = tree.arrays(library='pd')
# print(df[df['eventID'] == 25745])
# print(df[:nevent_printed])

# PrintInfo about 'coincidences'
tree = uproot.open(path + 'CC_Coincidences.root:Coincidences')
print(tree.num_entries, 'entries in tree Coincidences')
df = tree.arrays(library='pd')
print(df[:nentries_printed])

# PrintInfo about 'coincidence sequences'
tree = uproot.open(path + 'CC_sequenceCoincidence.root:sequenceCoincidence')
print(tree.num_entries, 'entries in tree sequenceCoincidence')
df = tree.arrays(library='pd')
print(df[:nentries_printed])

# # PrintInfo about 'cones' => comment out if cone tree was not created (has to be done after simulation)
tree = uproot.open(path + 'CC_Cones.root:Cones')
print(tree.num_entries, 'entries in tree Cones')
df = tree.arrays(library='pd')
print(df[:])
