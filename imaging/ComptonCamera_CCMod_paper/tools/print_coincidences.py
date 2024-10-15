import os
from operator import index
import pandas
import awkward as ak
import uproot
import numpy as np
pandas.set_option('display.max_columns', 100), pandas.set_option('display.width', 400), pandas.set_option(
    'display.max_rows', 1000)

path = '../output/test_data/'
#path = '/media/billoud/Volume/CT/GATE/LaBr3_adder_thl_100/'
nevent_printed = 10

# Print some info about 'singles' first
tree = uproot.open(path+'CC_Singles.root:Singles')
print(tree.num_entries, 'entries in tree Singles')
print(np.unique(tree["eventID"].array(library="np")).size, 'unique eventIDs')
df = tree.arrays(["eventID", "layerName", "time", "round(1000*energy)"],library='pd')
print(df[:nevent_printed])

# Print info about coincidences
tree = uproot.open(path+'CC_Coincidences.root:Coincidences')
print(tree.num_entries, 'entries in tree Coincidences')
df = tree.arrays(["eventID ", 'coincID', "layerName", "time", "round(1000*energy)"],
                #"eventID == 490019",
                 #"coincID == 10631",
                 library='pd')
print(df[:nevent_printed])
df_grouped = df.groupby('coincID')
coincSize = df_grouped.size()
for i in range(1, coincSize.max() + 1):
    print('number of coincidences with', i, 'singles:', len(coincSize[coincSize == i]), '(can be in same layer, can be from different events)' if i>1 else '(should be 0?)')
print(df_grouped.filter(lambda x: len(x) == 1)) # prints coincidences with 3 singles
print(df_grouped.filter(lambda x: len(x) == 3)) # prints coincidences with 3 singles