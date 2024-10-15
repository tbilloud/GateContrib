import matplotlib
import numpy as np

matplotlib.get_backend()
import matplotlib.pyplot as plt
import uproot

# Here I use Cones root files as input which are obtained with the GateDigit_seqCoinc2Cones executable
# This executable is compiled with the other offline processing tools but is not mentioned in the website or paper...
# Usage: GateDigit_seqCoinc2Cones CC_sequenceCoincidence.root CC_Cones.root
# There is a bug however: it requires the tree in CC_sequenceCoincidence.root to have a 'sublayerID' branch which is not
# present in the output of the GateDigit_seqCoincidence executable. Thus, I add a dummy column first with:
# path = '../output/test_data/'
# with uproot.recreate(path+'CC_sequenceCoincidence.root') as file:
#     df = tree.arrays(library='pd')
#     df['sublayerID'] = -1
#     file["sequenceCoincidence"] = df
#
#   From Gate source code:
#   G4double m_E1;            // energy deposition of the first interaction
#   G4double m_E2;            // energy deposition of the second interaction
#   G4double m_ER;            // Total energy deposition except E1
#
# From the paper:
# For the comparison with experimental data, the initial energy E0 was estimated from the sum of the energy deposition
# in the layers. When the total deposited energy was below 600 keV, E0 was assigned to the 511 keV photon and otherwise
# to the 1275 keV photon.

path = '../output/test_data/'
bins = [50, 50]

tree = uproot.open(path + 'CC_Cones.root:Cones')
print(tree.num_entries, 'entries in tree Cones')

def calculate_error(row):
    E0 = row['energyR'] + row['energy1']
    E0 = 0.511 if E0 < 0.6 else 1.275
    E1 = row['energy1']
    mc2 = 0.511
    cos_theta_C = 1 - (mc2 * E1) / (E0 * (E0 - E1))
    theta_C = np.arccos(cos_theta_C)

    g_10 = np.array([row['globalPosX1'], row['globalPosY1'], row['globalPosZ1']])
    g_21 = np.array([row['globalPosX2'], row['globalPosY2'], row['globalPosZ2']])
    dot_product = np.dot(g_10, g_21)
    magnitude_g_10 = np.linalg.norm(g_10)
    magnitude_g_21 = np.linalg.norm(g_21)
    cos_theta_G = dot_product / (magnitude_g_10 * magnitude_g_21)
    theta_G = 2 * np.arccos(cos_theta_G)

    return theta_G - theta_C


df = tree.arrays(library='pd')
df['error'] = df.apply(calculate_error, axis=1)
print(df[:5])
df_511 = df[df['energyR'] + df['energy1'] < 0.6]
df_1275 = df[df['energyR'] + df['energy1'] >= 0.6]

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(28, 5))
plot_args = dict(bins=100, range=(-2, 2), histtype='step', color='black', linestyle='dotted')
ax1.hist(df_511['error'], **plot_args)
ax2.hist(df_1275['error'], **plot_args)
ax3.hist(df['error'], **plot_args)
for ax in [ax1, ax2, ax3]:
    ax.set_ylabel('Counts')
    ax.set_xlabel(r'$\theta_G - \theta_C$ (rad)', loc='right')
plt.show()
