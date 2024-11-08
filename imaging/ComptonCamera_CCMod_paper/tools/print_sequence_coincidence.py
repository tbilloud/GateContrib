
import pandas
import uproot
pandas.set_option('display.max_columns', 100), pandas.set_option('display.width', 400), pandas.set_option(
    'display.max_rows', 1000)

path = '../output/test_data/'
nevent_printed = 10

# Print info about coincidence sequences
tree = uproot.open(path+'CC_sequenceCoincidence.root:sequenceCoincidence')
print(tree.num_entries, 'entries in tree sequenceCoincidence')
df_SC = tree.arrays(library='pd')
print(df_SC[:5])