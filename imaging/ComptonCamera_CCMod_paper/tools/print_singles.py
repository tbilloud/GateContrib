import os
from operator import index
import pandas
import awkward as ak
import uproot
import numpy as np

pandas.set_option('display.max_columns', 100), pandas.set_option('display.width', 400), pandas.set_option(
    'display.max_rows', 1000)

path = '../output/test_data/'

# Print info about singles
tree = uproot.open(path + 'CC_Singles.root:Singles')
print(tree.num_entries, 'entries in tree Singles')
df = tree.arrays(
    # ["eventID", "time", "sourceEnergy", "energyFinal", "layerName"],
    # 'eventID == 323',
    library='pd')
print(df[:])

# Extra info
# print(np.unique(tree["eventID"].array(library="np")).size, 'unique eventIDs')
