import uproot
import numpy as np

# Create root file with cone tree, as would be done by GateDigit_seqCoinc2Cones
# It also avoid bugs in GateDigit_seqCoinc2Cones:
#  - GateDigit_seqCoinc2Cones requires a sublayerID in the input file (sequenceCoincidence.root) which is not present in Gate 9.2
#  - the nSingles branch produced by GateDigit_seqCoinc2Cones has wrong values, i.e. only 1 instead of the number of singles in the coincidence
#  - GateDigit_seqCoinc2Cones seems not to work for any output file name
# ! WARNING ! For now, only works when adderComptPhotIdeal is used in the simulation

# Define the input and output file paths
input_file_path = "../sourcePoint_cameraSingle/output/CC_sequenceCoincidence.root"
output_file_path = "../sourcePoint_cameraSingle/output/CC_Cones.root"

# Open the input ROOT file and get the tree
with uproot.open(input_file_path) as file:
    tree = file["sequenceCoincidence"]

    # Read the necessary branches
    energy_ini = tree["energyIni"].array()
    energy_fin = tree["energyFinal"].array()
    global_pos_x = tree["globalPosX"].array()
    global_pos_y = tree["globalPosY"].array()
    global_pos_z = tree["globalPosZ"].array()
    event_id = tree["eventID"].array()
    run_id = tree["runID"].array()

# Initialize lists to store the calculated variables
energy1 = []
energyR = []
globalPosX1 = []
globalPosY1 = []
globalPosZ1 = []
globalPosX2 = []
globalPosY2 = []
globalPosZ2 = []
nSingles = []
IsTrueCoinc = []

# TODO: make this a function so that it can be reused in other scripts
# TODO: does not work when pile up

# Loop over the events and calculate the variables
for i in range(len(energy_ini)):
    if i == 0 or (event_id[i] != event_id[i-1] or run_id[i] != run_id[i-1]):
        energy1.append(energy_ini[i] - energy_fin[i])
        energyR.append(energy_fin[i])
        globalPosX1.append(global_pos_x[i])
        globalPosY1.append(global_pos_y[i])
        globalPosZ1.append(global_pos_z[i])
        first_event_id = event_id[i]
        is_true_coinc = True
        counter = 1
    else:
        if event_id[i] != first_event_id:
            is_true_coinc = False
        if counter == 1:
            globalPosX2.append(global_pos_x[i])
            globalPosY2.append(global_pos_y[i])
            globalPosZ2.append(global_pos_z[i])
        counter += 1

    if i == len(energy_ini) - 1 or (event_id[i] != event_id[i+1] or run_id[i] != run_id[i+1]):
        nSingles.append(counter)
        IsTrueCoinc.append(is_true_coinc)


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