import os
from operator import index
import pandas
import awkward as ak
import uproot
import numpy as np
from matplotlib.style.core import library
pandas.set_option('display.max_columns', 100), pandas.set_option('display.width', 400), pandas.set_option(
    'display.max_rows', 1000)

path = '../output/seed1_time100/'
#path = '/media/billoud/Volume/CT/GATE/LaBr3_adder_thl_100/'
nevent_printed = 10

# Print some info about 'singles' first
tree = uproot.open(path+'CC_Singles.root:Singles')
print(tree.num_entries, 'entries in tree Singles')
df = tree.arrays(["eventID", "layerName", "time", "round(1000*energy)"],library='pd')

# Print info about coincidences
tree = uproot.open(path+'CC_Coincidences.root:Coincidences')
print(tree.num_entries, 'entries in tree Coincidences')
df = tree.arrays(["eventID ", 'coincID', "layerName", "time", "round(1000*energy)"],library='pd')

# Print info about coincidence sequences
tree = uproot.open(path+'CC_sequenceCoincidence.root:sequenceCoincidence')
print(tree.num_entries, 'entries in tree sequenceCoincidence')
df_SC = tree.arrays(library='pd')
print(df_SC[:5])

# # Add dummy sublayerID to sequenceCoincidence
# with uproot.recreate(path+'CC_sequenceCoincidence_new.root') as file:
#     df = tree.arrays(library='pd')
#     df['sublayerID'] = -1
#     file["sequenceCoincidence"] = df
# tree_new = uproot.open(path+'CC_sequenceCoincidence_new.root:sequenceCoincidence')
# print(tree_new.keys())