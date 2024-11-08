import pandas
import uproot

pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 1000)

path = '../output/'
nevent_printed = 10

# Print some info about 'hist' => comment out if hit tree was not saved
tree = uproot.open(path + 'CC_Hits.root:Hits')
print(tree.num_entries, 'entries in tree Hits')
df = tree.arrays(library='pd')
print(df[df['eventID'] == 22819])

# Print some info about 'singles'
tree = uproot.open(path + 'CC_Singles.root:Singles')
print(tree.num_entries, 'entries in tree Singles')
df = tree.arrays(library='pd')
print(df[:5])

# Print info about coincidences
tree = uproot.open(path + 'CC_Coincidences.root:Coincidences')
print(tree.num_entries, 'entries in tree Coincidences')
df = tree.arrays(library='pd')
print(df[:5])

# Print info about coincidence sequences
tree = uproot.open(path + 'CC_sequenceCoincidence.root:sequenceCoincidence')
print(tree.num_entries, 'entries in tree sequenceCoincidence')
df = tree.arrays(library='pd')
print(df[:5])

# Print info about cones => comment out if cone tree was not created (has to be done after simulation)
tree = uproot.open(path + 'CC_Cones.root:Cones')
print(tree.num_entries, 'entries in tree Cones')
df = tree.arrays(library='pd')
print(df[:5])