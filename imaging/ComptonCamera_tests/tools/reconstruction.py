import napari
from pathlib import Path
from imaging.ComptonCamera_tests.Gate9.tools.seqCoinc2Cones import *
from imaging.ComptonCamera_tests.Gate10.tools.analysis_cones import *
from imaging.ComptonCamera_tests.tools.compton import compton_forward
from imaging.ComptonCamera_tests.tools.utils import remove_nans, coordinateOrigin2arrayCenter

cp.set_printoptions(linewidth=200)

# Script to reconstruct 3D image from cones

# Units should be the same in cones_array and vpitch
def reconstruct(cones_array, vsize, vpitch):

    # Coordinate system
    print(cones_array)
    cones_array = coordinateOrigin2arrayCenter(cones_array, vpitch, vsize)

    vol_init = cp.zeros(vsize, dtype=cp.float32)
    vol = compton_forward(volume=vol_init, cones=cones_array, volume_pitch=vpitch)

    vol /= vol.max()
    vol = vol.get()
    cp.save(fname / "reconstruction.npy", vol)
    vargs = dict(translate=(-vsize[0] // 2, -vsize[1] // 2, -vsize[2] // 2), axis_labels=["y", "x", "z"],
                 colormap='gray_r')
    viewer = napari.view_image(vol, **vargs)
    viewer.axes.visible = True
    # TODO: add cuboid representing th detector (see napari's bounding box / annotation plugin?)
    napari.run()

    # ##############################################################
    # # Display results
    # ##############################################################
    # vargs = dict(translate=(-vsize[0] // 2, -vsize[1] // 2), axis_labels=["cone number", "x", "y"])
    # viewer = napari.view_image(np.asarray(z_slice_stack), **vargs)
    # viewer.axes.visible = True
    # napari.run()
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
    fname, E0_MeV = Path('../Gate10/output'), 1.0
    cones_array = hits2cones_withDepth_byEventID(fname / 'CC_Hits.root', E0_MeV)

    # ###### Preprocessing #########
    print('number of cones with a nan value:', cp.isnan(cones_array).any(axis=1).sum())
    # print(len(cones_array), 'cones before removing nans')
    # cones_array = remove_nans(cones_array)
    # print(len(cones_array), 'cones after removing nans')

    # Volume size and pitch
    vsize = (256, 256, 256)
    vpitch = 7.8125
    
    reconstruct(cones_array, vsize, vpitch)