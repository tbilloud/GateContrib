import uproot
import cupy as cp
from seqCoinc2Cones import seqCoinc2Cones


# Create cupy array file with cones from sequenceCoincidence root file
# TODO: For now, only works when adderComptPhotIdeal is used in the simulation
#       => energyR is not used and user has to set E0 instead

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
    print('values/counts in TBranch nSingles', cp.unique(cp_array[:, 6].astype(cp.int32), return_counts=True))
    print('values/counts in TBranch IsTrueCoinc', cp.unique(cp_array[:, 7].astype(cp.int32), return_counts=True))
    print(cp_array.shape[0], 'cones before filtering')
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


# Takes array of array with 10 columns:
# energy1, energyR, globalPosX1, globalPosY1, globalPosZ1, globalPosX2, globalPosY2, globalPosZ2, nSingles, IsTrueCoinc
# And returns array with 8 columns:
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
    dict_branches = tree.arrays(library='np')
    del dict_branches['energyR']

    cp_array = cp.stack([cp.array(dict_branches[key]) for key in dict_branches.keys()], axis=-1)

    cp_array = filter_conesArray(cp_array, filter_TrueCoinc, nSingles_max)

    cp_array = conesGate2cones(E0_MeV, cp_array, er)

    cp_array = coordinateOrigin2arrayCenter(cp_array, vpitch, vsize)

    return cp_array
