import matplotlib.pyplot as plt
import pandas as pd
import uproot
import numpy as np

pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 400)
pd.set_option('display.max_rows', 1000)

# Script to plot doppler broadening
# Slower than using sequenceCoincidence tree

path = '/imaging/ComptonCamera_tests/ideal/output/'
nentries_printed = 1000 # None to read all entries

tree = uproot.open(path + 'CC_Hits.root:Hits')
print(tree.num_entries, 'entries in tree Hits')
df = tree.arrays(library='pd', entry_stop=nentries_printed)

# keep only entries belonging to a group of exactly 2 with same eventID and one has postStepProcess == 'compt' and the other has postStepProcess == 'phot', knowing that postStepProcess can also be Rayl
df['postStepProcess'] = df['postStepProcess'].astype(str)
df = df.groupby('eventID').filter(lambda x: len(x) == 2 and 'compt' in x['postStepProcess'].values and 'phot' in x['postStepProcess'].values)
print('grouped')

def calculate_angle(row):
    posX, posY, posZ = 'posX', 'posY', 'posZ'
    vector1 = np.array([row.iloc[0][posX], row.iloc[0][posY], row.iloc[0][posZ]])
    vector2 = np.array([row.iloc[1][posX], row.iloc[1][posY], row.iloc[1][posZ]])
    dot_product = np.dot(vector1, vector2)
    norm1 = np.linalg.norm(vector1)
    norm2 = np.linalg.norm(vector2)
    angle = np.arccos(dot_product / (norm1 * norm2))
    return np.degrees(angle)

# Group by eventID and calculate the angle for each group
result = df.groupby('eventID').apply(lambda x: pd.Series({
    'eventID': x['eventID'].iloc[0],
    'angle': calculate_angle(x),
    'edep': x['edep'].iloc[0]
})).reset_index(drop=True)
result['eventID'] = result['eventID'].astype(int)

print(len(result),'good events')
print(result)

# plot histogram of angles
plt.hist(result['angle'], bins=100)
plt.show()