import sys

import cupy as cp
import numpy as np
import uproot


# Function to create cones from sequenceCoincidence root files, as would be done by GateDigit_seqCoinc2Cones
# Not only CC_Cones.tree can be created, but also numpy arrays and in different formats
# It also avoid bugs in GateDigit_seqCoinc2Cones:
#  - GateDigit_seqCoinc2Cones requires a sublayerID in the input file (sequenceCoincidence.root) which is not present in Gate 9.2
#  - the nSingles branch produced by GateDigit_seqCoinc2Cones has wrong values, i.e. only 1 instead of the number of singles in the coincidence
#  - GateDigit_seqCoinc2Cones seems not to work for any output file name
# TODO: For now, only works when adderComptPhotIdeal is used in the simulation
#       => energyR is not used and user has to set E0 instead


# ##################### MAIN FUNCTION ###################################
# Inspired by GateSequenceCoincidenceTreeReader.cc in Gate 9.2 source code #
# Read sequenceCoincidence tree and return lists with parameters needed for cone reconstruction
# TODO: test if this works with multiple runs
# TODO: make it work for actors other than Gate9.2
# TODO: make it faster ! (few seconds for 100k cones for now)
def seqCoinc2Cones(input_file_path, nentries=None):
    # Open the input ROOT file and get the tree
    with uproot.open(input_file_path) as file:
        tree = file["sequenceCoincidence"]
        print('-' * 100)
        print('Processing', input_file_path)
        print(tree.num_entries, 'entries in tree sequenceCoincidence, reading', nentries if nentries else 'all')
        print('Number of cones might be lower than n_entries / 2 if there are coincidence groups with > than 2 singles')
        if nentries and nentries > tree.num_entries:
            sys.exit('Error: nentries is more than the number of entries in the tree')

        # Read the necessary branches
        energy_ini = tree["energyIni"].array(entry_stop=nentries)
        energy_fin = tree["energyFinal"].array(entry_stop=nentries)
        global_pos_x = tree["globalPosX"].array(entry_stop=nentries)
        global_pos_y = tree["globalPosY"].array(entry_stop=nentries)
        global_pos_z = tree["globalPosZ"].array(entry_stop=nentries)
        event_id = tree["eventID"].array(entry_stop=nentries)
        run_id = tree["runID"].array(entry_stop=nentries)
        coinc_id = tree["coincID"].array(entry_stop=nentries)

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

    # Initialize variables
    first_event_id = None
    counter = 0

    # Loop over the events and calculate the variables
    last_entry = nentries if nentries else tree.num_entries
    for i in range(last_entry):
        if i == 0 or (coinc_id[i] != coinc_id[i - 1] or run_id[i] != run_id[i - 1]):
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

        if i == last_entry - 1 or (coinc_id[i] != coinc_id[i + 1] or run_id[i] != run_id[i + 1]):
            nSingles.append(counter)
            IsTrueCoinc.append(is_true_coinc)

    # When nentries is used, the loop might stop right after appending the first element of the coincidence sequence,
    # i.e. before position 2 of that coincidence is filled, resulting in globalPosXYZ2 to be shorter than other lists.
    # It is then necessary to remove the last element of the other lists to make them all the same length.
    energy1 = energy1[:len(globalPosX2)]
    energyR = energyR[:len(globalPosX2)]
    globalPosX1 = globalPosX1[:len(globalPosX2)]
    globalPosY1 = globalPosY1[:len(globalPosX2)]
    globalPosZ1 = globalPosZ1[:len(globalPosX2)]
    nSingles = nSingles[:len(globalPosX2)]
    IsTrueCoinc = IsTrueCoinc[:len(globalPosX2)]

    return [energy1, energyR, globalPosX1, globalPosY1, globalPosZ1, globalPosX2, globalPosY2, globalPosZ2, nSingles,
            IsTrueCoinc]


def seqCoinc2ConesTTree(input_file_path, output_file_path, nentries=None):
    # Open the input ROOT file and get the tree
    print(f"Reading TTree 'sequenceCoincidence' from {input_file_path}")
    energy1, energyR, globalPosX1, globalPosY1, globalPosZ1, globalPosX2, globalPosY2, globalPosZ2, nSingles, IsTrueCoinc = seqCoinc2Cones(
        input_file_path, nentries=nentries)

    # Write the calculated variables to the output ROOT file
    print(f"Writing TTree 'Cones' to {output_file_path}")
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


# Create cupy array file with cones from sequenceCoincidence root file
def seqCoin2ConesArray(input_path, E0, vsize, vpitch, inv_cos_error, nSingles_max=False, filter_TrueCoinc=False,
                       nentries=None):
    cp_array = cp.stack([cp.array(list) for list in seqCoinc2Cones(input_path, nentries)], axis=-1)
    # energy1, energyR, globalPosX1, globalPosY1, globalPosZ1, globalPosX2, globalPosY2, globalPosZ2, nSingles, IsTrueCoinc
    cp_array = cp_array[:, [0, 2, 3, 4, 5, 6, 7, 8, 9]]  # TODO: this removes energyR, will have to be added back

    cp_array = filter_conesArray(cp_array, filter_TrueCoinc, nSingles_max)

    cp_array = conesGate2cones(E0, cp_array, inv_cos_error)

    cp_array = coordinateOrigin2arrayCenter(cp_array, vpitch, vsize)

    return cp_array


def filter_conesArray(cp_array, filter_TrueCoinc, nSingles_max):
    print(cp_array.shape[0], 'cones before filtering')
    print('values/counts in TBranch nSingles', cp.unique(cp_array[:, 7].astype(cp.int32), return_counts=True))
    print('values/counts in TBranch IsTrueCoinc', cp.unique(cp_array[:, 8].astype(cp.int32), return_counts=True))
    if nSingles_max:
        cp_array = cp_array[cp_array[:, 7] <= nSingles_max]
    if filter_TrueCoinc:
        cp_array = cp_array[cp_array[:, 8] == 1]
    print(cp_array.shape[0], 'cones after filtering')
    return cp_array


def coordinateOrigin2arrayCenter(cp_array, vpitch, vsize):
    cp_array[:, 0] = cp_array[:, 0] + vpitch * vsize[0] / 2
    cp_array[:, 1] = cp_array[:, 1] + vpitch * vsize[1] / 2
    cp_array[:, 2] = cp_array[:, 2] + vpitch * vsize[2] / 2
    return cp_array


# Convert cones array from Gate format, i.e. with 10 columns:
# energy1, energyR, globalPosX1, globalPosY1, globalPosZ1, globalPosX2, globalPosY2, globalPosZ2, nSingles, IsTrueCoinc
# to array with 8 columns:
# apex_x, y, z, normalized_direction_x, y, z, cosine_of_cone_half_angle, inverse_of_cosine_error
def conesGate2cones(E0, cp_array, inv_cos_error):
    vectorX = cp_array[:, 1] - cp_array[:, 4]
    vectorY = cp_array[:, 2] - cp_array[:, 5]
    vectorZ = cp_array[:, 3] - cp_array[:, 6]
    magnitude = cp.sqrt(vectorX ** 2 + vectorY ** 2 + vectorZ ** 2)
    nX = vectorX / magnitude
    nY = vectorY / magnitude
    nZ = vectorZ / magnitude
    cosT = 1 - (0.511 * cp_array[:, 0]) / (E0 * (E0 - cp_array[:, 0]))
    inv_cos_error = inv_cos_error * cp.ones_like(cosT)
    cp_array = cp.stack([cp_array[:, 1], cp_array[:, 2], cp_array[:, 3], nX, nY, nZ, cosT, inv_cos_error], axis=-1)
    # [ apex_x, y, z, normalized_direction_x, y, z, cosine_of_cone_half_angle, inverse_of_cosine_error]
    return cp_array


def conesTTree2conesArray(input_file_path, E0_MeV, vsize, vpitch, er, nSingles_max=2, filter_TrueCoinc=False,
                          nentries=None):
    tree = uproot.open(input_file_path)['Cones']
    print('Processing', input_file_path, 'with', tree.num_entries, 'entries')
    dict_branches = tree.arrays(library='np', entry_stop=nentries)
    del dict_branches['energyR']

    cp_array = cp.stack([cp.array(dict_branches[key]) for key in dict_branches.keys()], axis=-1)

    cp_array = filter_conesArray(cp_array, filter_TrueCoinc, nSingles_max)

    cp_array = conesGate2cones(E0_MeV, cp_array, er)

    cp_array = coordinateOrigin2arrayCenter(cp_array, vpitch, vsize)

    return cp_array
