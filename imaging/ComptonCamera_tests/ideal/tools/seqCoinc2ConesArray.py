import uproot
import cupy as cp
from seqCoinc2Cones import seqCoinc2Cones

# Create cupy array file with cones from sequenceCoincidence root file
# ! WARNING ! For now, only works when adderComptPhotIdeal is used in the simulation

def seqCoin2ConesArray(input_file_path, E0, vsize, vpitch, inv_cos_error, nSingles_max=False, filter_TrueCoinc=False, nentries = None):

    energy1, energyR, globalPosX1, globalPosY1, globalPosZ1, globalPosX2, globalPosY2, globalPosZ2, nSingles, IsTrueCoinc = seqCoinc2Cones(input_file_path, nentries)

    # If filtering nSingles and IsTrueCoinc is needed
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