import pandas
import uproot
import numpy as np

pandas.set_option('display.max_columns', 100), pandas.set_option('display.width', 400), pandas.set_option(
    'display.max_rows', 1000)

# path = '../output/test_data'
path = '/media/billoud/Volume/CT/GATE/seed1_time100/'

# Print info about hits
tree_hits = uproot.open(path + 'CC_Hits.root:Hits')
print(tree_hits.num_entries, 'entries in tree Hits')
df = tree_hits.arrays(
    # ["eventID", "PDGEncoding", "trackID", "parentID", "time", "edep", "stepLength", "sourceEnergy"],
    # 'eventID == 323',
    library='pd',
    entry_start=0,
    entry_stop=10, # None for all entries
)
print(df[:])

# Extra info
# print(np.unique(tree_hits["eventID"].array(library="np")).size, 'unique eventIDs')
# print(np.unique(tree_hits["trackID"].array(library="np")).size, 'unique trackIDs')
# print(np.unique(tree_hits["parentID"].array(library="np")).size, 'unique parentIDs')
# print(df['sourceEnergy'].unique())
