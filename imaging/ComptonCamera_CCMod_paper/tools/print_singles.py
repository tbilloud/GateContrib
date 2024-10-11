import os
from operator import index
import pandas
import awkward as ak
import uproot
import numpy as np

pandas.set_option('display.max_columns', 100), pandas.set_option('display.width', 400), pandas.set_option(
    'display.max_rows', 1000)

print(uproot.open('../output/temp/CC_Singles.root').keys())
tree = uproot.open('../output/CC_Singles.root:Singles')
print(tree.num_entries, 'entries in tree Singles')
print(np.unique(tree["eventID"].array(library="np")).size, 'unique eventIDs')

df = tree.arrays(
    ["eventID", "time", "sourceEnergy", "energyFinal", "layerName"],
    # 'eventID == 323',
    library='pd')
print(df[:20])
# print(df['eventID'].unique()) # 153  250  299  323  333  388  464  586  604  624  672
print(df['sourceEnergy'].unique())