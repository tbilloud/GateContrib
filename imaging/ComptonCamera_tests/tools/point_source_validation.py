import matplotlib.pyplot as plt
import napari
from pathlib import Path
from imaging.ComptonCamera_tests.Gate9.tools.seqCoinc2Cones import *
from imaging.ComptonCamera_tests.Gate10.tools.analysis_cones import *
from imaging.ComptonCamera_tests.tools.compton import compton_forward
from imaging.ComptonCamera_tests.tools.utils import remove_nans, coordinateOrigin2arrayCenter

cp.set_printoptions(linewidth=200)


# Script to check the precision of Gate9 or Gate10 simulations with a point source
# Can be run as a standalone script or (WIP) as a function in a Gate10 script

# All cones should intersect at the source point
# Possible reasons for bad cones:
# - rayleigh scattering
# - compton scattering with electron not at rest (doppler broadening)
# - particle-induced X-ray emission (fluorescence, Auger)
# - more than 2 coincident events (nSingles)
# - electron/gamma escape
# - time resolution (pile-up, singles with different eventID, true_coinc)
# - energy/spatial resolution

# Units should be the same in cones_array, vpitch and source_pos
def point_source_cone_validation(cones_array, world_z, source_pos, plot = False):

    # Volume size and pitch
    vsize = (256, 256, 256)
    vpitch = world_z / vsize[2]
    vol_init = cp.zeros(vsize, dtype=cp.float32)

    # Source position must be in units of voxels in vol
    source_pos_in_voxels = [int(source_pos[i] / vpitch) + (vsize[i] // 2) for i in range(3)]

    # Format cones array
    cones_array, EventID = cones_array[:, 1:], cones_array[:, 0]

    # Coordinate system
    cones_array = coordinateOrigin2arrayCenter(cones_array, vpitch, vsize)

    # ######## RECONSTRUCT CONE BY CONE #######################################
    z_slice_stack = list()
    n_bad_cones = 0
    # for i, cone in enumerate(cones_array):
    for cone,event in zip(cones_array,EventID):
        vol = compton_forward(volume=vol_init, cones=cone, volume_pitch=vpitch)
        z_slice = vol[:, :, source_pos_in_voxels[2]]
        z_slice_stack.append(z_slice.get())
        if z_slice[source_pos_in_voxels[0], source_pos_in_voxels[1]] == 0:
            # TODO sometime cone is bad but z_slice is not 0
            n_bad_cones += 1

        # ##############################################################
        # # Display stack with matplotlib (one by one)
        # ##############################################################
        if plot:
            plt.imshow(z_slice.get(), cmap='gray')
            plt.scatter(source_pos_in_voxels[0], source_pos_in_voxels[1], c='r', s=10)
            plt.scatter(vsize[0]//2,vsize[1]//2, c='b', s=10)
            plt.title(f'EventID: {int(event)}')
            plt.colorbar()
            plt.show()

    print(n_bad_cones, 'bad cones')

    # ##############################################################
    # # Display stack with napari (scrolling)
    # ##############################################################
    # vargs = dict(translate=(-vsize[0] // 2, -vsize[1] // 2), axis_labels=["cone number", "x", "y"])
    # viewer = napari.view_image(np.asarray(z_slice_stack), **vargs)
    # viewer.axes.visible = True
    # napari.run()
    return z_slice_stack


if __name__ == "__main__":
    # ###### READING Gate9.2 sequenceCoincidence.root files ##############
    # fname, E0_MeV, world_z, source_pos = Path('../Gate9/output'), 0.140, 200, [0, 0, 0]
    # nSingles_max = False  # maximum number of singles per coincidence, False to disable
    # true_coinc = False  # filter true coincidences (i.e. avoid singles from different events)
    # nentries = None  # None to read all entries
    # cones_array = seqCoin2ConesArray(fname / 'CC_sequenceCoincidence.root', E0_MeV, vsize, vpitch, er, nSingles_max, true_coinc, nentries)

    # ###### READING Gate9.2 CC_Cones.root files #########################
    # fname, E0_MeV, world_z, source_pos = Path('../Gate9/output'), 0.140, 200, [0, 0, 0]
    # nSingles_max = False  # maximum number of singles per coincidence, False to disable
    # true_coinc = False  # filter true coincidences (i.e. avoid singles from different events)
    # nentries = None  # None to read all entries
    # cones_array = conesTTree2conesArray(fname / 'CC_Cones.root', E0_MeV, er, nSingles_max, true_coinc, nentries)

    # ###### READING Gate10 hit root files ##############
    fname, E0_MeV, world_z, source_pos = Path('../Gate10/output'), 1.0, 200, [0, 0, -50]
    cones_array = hits2cones_byEventID(fname / 'CC_Hits.root', E0_MeV)

    # ###### Preprocessing #########
    # print('number of cones with a nan value:', cp.isnan(cones_array).any(axis=1).sum())
    # print(len(cones_array), 'cones before removing nans')
    # cones_array = remove_nans(cones_array)
    # print(len(cones_array), 'cones after removing nans')

    point_source_cone_validation(cones_array, world_z, source_pos)
