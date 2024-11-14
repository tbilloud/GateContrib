import uproot
import numpy as np
from seqCoinc2Cones import seqCoinc2Cones

# Create root file with cone tree, as would be done by GateDigit_seqCoinc2Cones
# It also avoid bugs in GateDigit_seqCoinc2Cones:
#  - GateDigit_seqCoinc2Cones requires a sublayerID in the input file (sequenceCoincidence.root) which is not present in Gate 9.2
#  - the nSingles branch produced by GateDigit_seqCoinc2Cones has wrong values, i.e. only 1 instead of the number of singles in the coincidence
#  - GateDigit_seqCoinc2Cones seems not to work for any output file name
# ! WARNING ! For now, only works when adderComptPhotIdeal is used in the simulation

# Define the input and output file paths
input_file_path = "../sourcePoint_cameraSingle/output/CC_sequenceCoincidence.root"
output_file_path = "../sourcePoint_cameraSingle/output/CC_Cones.root"
nentries = None # None to read all entries

# Open the input ROOT file and get the tree
energy1, energyR, globalPosX1, globalPosY1, globalPosZ1, globalPosX2, globalPosY2, globalPosZ2, nSingles, IsTrueCoinc = seqCoinc2Cones(
    input_file_path, nentries=nentries)

# Write the calculated variables to the output ROOT file
with uproot.recreate(output_file_path) as file:
    file["Cones"] = {
        "energy1": np.array(energy1),
        "energyR": np.array(energyR),
        "globalPosX1": np.array(globalPosX1),
        "globalPosY1": np.array(globalPosY1),
        "globalPosZ1": np.array(globalPosZ1),
        "globalPosX2": np.array(globalPosX2),
        "globalPosY2": np.array(globalPosY2),
        "globalPosZ2": np.array(globalPosZ2),
        "nSingles": np.array(nSingles),
        "IsTrueCoinc": np.array(IsTrueCoinc)
    }