import uproot
import cupy as cp

# Create cupy array file with cones from sequenceCoincidence root file
# ! WARNING ! For now, only works when adderComptPhotIdeal is used in the simulation
# TODO: make this a function so that it can be reused in other scripts
# TODO: test if this works with multiple runs
# TODO: make it work for actors other than ideal

def seqCoin2Cones(input_file_path, E0, vsize, vpitch, inv_cos_error, nSingles_max=False, filter_TrueCoinc=False, nentries = None):

    # Open the input ROOT file and get the tree
    with uproot.open(input_file_path) as file:
        tree = file["sequenceCoincidence"]
        print('-'*100)
        print(tree.num_entries, 'entries in tree sequenceCoincidence, reading', nentries if nentries else 'all')

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
    print('last_entry', last_entry)
    for i in range(last_entry):
        if i == 0 or (coinc_id[i] != coinc_id[i-1] or run_id[i] != run_id[i-1]):
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

        if i == last_entry - 1 or (coinc_id[i] != coinc_id[i+1] or run_id[i] != run_id[i+1]):
            nSingles.append(counter)
            IsTrueCoinc.append(is_true_coinc)

    # When nentries is used, the loop might stop right after appending the first element of the coincidence sequence,
    # i.e. before position 2 of that coincidence is filled, resulting in globalPosXYZ2 to be shorter than other lists.
    energy1 = energy1[:len(globalPosX2)]
    energyR = energyR[:len(globalPosX2)]
    globalPosX1 = globalPosX1[:len(globalPosX2)]
    globalPosY1 = globalPosY1[:len(globalPosX2)]
    globalPosZ1 = globalPosZ1[:len(globalPosX2)]
    nSingles = nSingles[:len(globalPosX2)]
    IsTrueCoinc = IsTrueCoinc[:len(globalPosX2)]

    # If filtering nSingles and IsTrueCoinc is needed
    print(len(energy1), len(globalPosX1), len(globalPosY1), len(globalPosZ1), len(globalPosX2), len(globalPosY2), len(globalPosZ2), len(nSingles), len(IsTrueCoinc))
    cp_array = cp.stack([cp.array(energy1), cp.array(globalPosX1), cp.array(globalPosY1), cp.array(globalPosZ1), cp.array(globalPosX2), cp.array(globalPosY2), cp.array(globalPosZ2), cp.array(nSingles), cp.array(IsTrueCoinc)], axis=-1)
    print('values/counts in TBranch nSingles',cp.unique(cp.array(nSingles, dtype=cp.int32), return_counts=True))
    print('values/counts in TBranch IsTrueCoinc',cp.unique(cp.array(IsTrueCoinc, dtype=cp.int32), return_counts=True))
    print(cp_array.shape[0], 'cones before filtering')
    # remove rows where nSingles is more than parameter nSinglemax
    if nSingles_max:
        cp_array = cp_array[cp_array[:, 7] <= nSingles_max]
    if filter_TrueCoinc:
        cp_array = cp_array[cp_array[:, 8] == 1]
    print(cp_array.shape[0], 'cones after filtering')

    # If filtering nSingles and IsTrueCoinc is not needed
    # cp_array = cp.stack([cp.array(energy1), cp.array(globalPosX1), cp.array(globalPosY1), cp.array(globalPosZ1), cp.array(globalPosX2), cp.array(globalPosY2), cp.array(globalPosZ2)], axis=-1)

    ##############################################################
    # Convert data to standard cone parameters
    ##############################################################
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

    ##############################################################
    # Move origin to volume center
    ##############################################################
    cp_array[:, 0] = cp_array[:, 0] + vpitch * vsize[0] / 2
    cp_array[:, 1] = cp_array[:, 1] + vpitch * vsize[1] / 2
    cp_array[:, 2] = cp_array[:, 2] + vpitch * vsize[2] / 2

    return cp_array