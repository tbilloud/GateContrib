import os
from operator import index
import pandas
import awkward as ak
import uproot
import numpy as np
pandas.set_option('display.max_columns', 100), pandas.set_option('display.width', 400), pandas.set_option(
    'display.max_rows', 1000)

print(uproot.open('../output/temp/CC_Hits.root').keys())
tree_hits = uproot.open('../output/CC_Hits.root:Hits')
print(tree_hits.num_entries, 'entries in tree Hits')
print(np.unique(tree_hits["eventID"].array(library="np")).size, 'unique eventIDs')
print(np.unique(tree_hits["trackID"].array(library="np")).size, 'unique trackIDs')
print(np.unique(tree_hits["parentID"].array(library="np")).size, 'unique parentIDs')

df = tree_hits.arrays(
    ["eventID", "PDGEncoding", "trackID", "parentID", "time", "edep", "stepLength", "sourceEnergy",
     "energyFinal", "energyIniT", "postStepProcess", "processName", "layerName"],
    #'eventID == 323',
    library='pd')
print(df[:100])
# print(df['eventID'].unique()) # 153  250  299  323  333  388  464  586  604  624  672
print(df['sourceEnergy'].unique())