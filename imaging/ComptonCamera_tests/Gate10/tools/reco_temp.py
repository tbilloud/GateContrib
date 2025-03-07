# Script to reconstruct 3D image from cones

from pathlib import Path
from tools.analysis_cones import *
from imaging.ComptonCamera_tests.tools.compton import compton_forward
from tools.display_reconstruction import display_reconstruction

# Units should be the same in cones_array and vpitch
def reconstruct(cones_array, vpitch, vsize=(256, 256, 256), output=False,
                napari=False, det=False):

    vol = compton_forward(volume=cp.zeros(vsize, dtype=cp.float32), cones=cones_array, volume_pitch=vpitch)
    vol = (vol / vol.max())
    vol = vol.get()

    if output:
        cp.save(output, vol)
    if napari:
        display_reconstruction(vol, vsize, vpitch, det)

    return vol


if __name__ == "__main__":
    # ###### READING Gate9.2 sequenceCoincidence.root files ##############
    # fname, E0_MeV = Path('../Gate9/output'), 0.140
    # nSingles_max = False  # maximum number of singles per coincidence, False to disable
    # true_coinc = False  # filter true coincidences (i.e. avoid singles from different events)
    # nentries = None  # None to read all entries
    # cones_array = seqCoin2ConesArray(fname / 'CC_sequenceCoincidence.root', E0_MeV, vsize, vpitch, er, nSingles_max, true_coinc, nentries)

    # ###### READING Gate9.2 CC_Cones.root files #########################
    # fname, E0_MeV = Path('../Gate9/output'), 0.140
    # nSingles_max = False  # maximum number of singles per coincidence, False to disable
    # true_coinc = False  # filter true coincidences (i.e. avoid singles from different events)
    # nentries = None  # None to read all entries
    # cones_array = conesTTree2conesArray(fname / 'CC_Cones.root', E0_MeV, er, nSingles_max, true_coinc, nentries)

    # ###### READING Gate10 hit root files ##############
    fname, E0_MeV = Path('../output'), 1.0
    cones_array = gHits2cones_byEvtID(fname / 'CC_Hits.root', E0_MeV)

    # ###### Preprocessing #########
    print('number of cones with a nan value:', cp.isnan(cones_array).any(axis=1).sum())
    # print(len(cones_array), 'cones before removing nans')
    # cones_array = remove_nans(cones_array)
    # print(len(cones_array), 'cones after removing nans')

    reconstruct(cones_array, vpitch=1, output=False, napari=True)
