import os
from operator import index
import pandas
import awkward as ak
import uproot
import numpy as np
from matplotlib.style.core import library
pandas.set_option('display.max_columns', 100), pandas.set_option('display.width', 400), pandas.set_option(
    'display.max_rows', 1000)

path = '../output/test_data/'
#path = '/media/billoud/Volume/CT/GATE/LaBr3_adder_thl_100/'
nevent_printed = 10

# Print some info about 'singles' first
tree = uproot.open(path+'CC_Cones.root:Cones')
print(tree.num_entries, 'entries in tree Cones')
df = tree.arrays(library='pd')

print(df[:5])
#print(tree.num_entries, 'entries in tree Singles')

