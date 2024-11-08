import pandas
import uproot

pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 1000)

path = '../output/'
nevent_printed = 10

# Not processing Hits tree because I don't always save it (very large file)

# Print some info about 'singles' first
tree = uproot.open(path + 'CC_Singles_new.root:Singles')
print(tree.num_entries, 'entries in tree Singles')
df = tree.arrays(["eventID", "layerName", "time", "round(1000*energy)"], library='pd')

# Print info about coincidences
tree = uproot.open(path + 'CC_Coincidences.root:Coincidences')
print(tree.num_entries, 'entries in tree Coincidences')
df = tree.arrays(["eventID ", 'coincID', "layerName", "time", "round(1000*energy)"], library='pd')

# Print info about coincidence sequences
tree = uproot.open(path + 'CC_sequenceCoincidence.root:sequenceCoincidence')
print(tree.num_entries, 'entries in tree sequenceCoincidence')
df = tree.arrays(library='pd')
print(df[:5])

# Print info about cones
tree = uproot.open(path + 'CC_Cones.root:Cones')
print(tree.num_entries, 'entries in tree Cones')
df = tree.arrays(library='pd')
print(df[:5])