import uproot

# Read sequenceCoincidence tree and return lists with parameters needed for cone reconstruction
# TODO: test if this works with multiple runs
# TODO: make it work for actors other than ideal
# TODO: make it faster !
def seqCoinc2Cones(input_file_path, nentries=None):
    # Open the input ROOT file and get the tree
    with uproot.open(input_file_path) as file:
        tree = file["sequenceCoincidence"]
        print('-'*100)
        print('Processing',input_file_path)
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

    return [energy1, energyR, globalPosX1, globalPosY1, globalPosZ1, globalPosX2, globalPosY2, globalPosZ2, nSingles, IsTrueCoinc]