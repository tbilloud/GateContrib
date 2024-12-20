import napari
from pathlib import Path
from imaging.ComptonCamera_tests.ideal.tools.seqCoinc2Cones import *
from imaging.ComptonCamera_tests.tools.compton import compton_forward
from imaging.ComptonCamera_tests.tools.utils import remove_nans
cp.set_printoptions(linewidth=200)

# Script to check the precision of Gate9.2 simulation with point source
# All cones should intersect at the source point
# Possible reasons for bad cones:
# - rayleigh scattering
# - compton scattering with electron not at rest (doppler broadening)
# - particle-induced X-ray emission (fluorescence, Auger)
# - more than 2 coincident events (nSingles)
# - electron/gamma escape
# - time resolution (pile-up, singles with different eventID, true_coinc)
# - energy/spatial resolution

##############################################################
# Settings
##############################################################
fname, E0_MeV, world_mm = Path('../output'), 0.140, 200

vsize = (256, 256, 256)
vpitch = world_mm / vsize[2]
er = 200  # inverse of cosine error
nSingles_max = False  # maximum number of singles per coincidence, False to disable
true_coinc = False  # filter true coincidences (i.e. avoid singles from different events)
nentries = 1000  # None to read all entries
source_pos = [vsize[0] // 2,vsize[1] // 2,vsize[2] // 2] # in units of voxels in vol

##############################################################
# Do Projection
##############################################################
# ###### READING sequenceCoincidence.root files ##############
cones = seqCoin2ConesArray(fname / 'CC_sequenceCoincidence.root', E0_MeV, vsize, vpitch, er, nSingles_max, true_coinc, nentries)
# ###### READING CC_Cones.root files #########################
# cones = conesTTree2conesArray(fname / 'CC_Cones.root', E0_MeV, vsize, vpitch, er, nSingles_max, true_coinc, nentries)
# ######## RECONSTRUCT #######################################
print(len(cones), 'cones before removing nans')
cones = remove_nans(cones)
print(len(cones), 'cones after removing nans')
z_slice_stack = list()
n_bad_cones = 0
for i, cone in enumerate(cones):
    vol = cp.zeros(vsize, dtype=cp.float32)
    vol = compton_forward(volume=vol, cones=cone, volume_pitch=vpitch)
    # TODO: i've seen cases where 'cones' variable name was impacting 'compton_forward'
    z_slice = vol[:, :, source_pos[2]]
    # z_slice = cp.nan_to_num(z_slice)
    # z_slice[z_slice < 0] = 0
    # z_slice /= z_slice.max()
    z_slice_stack.append(z_slice.get())
    if z_slice[source_pos[0],source_pos[1]] == 0:
        n_bad_cones += 1
        print('bad cone at coincID', i, '(if no cone was filtered)')
print(n_bad_cones, 'bad cones')

##############################################################
# Display results
##############################################################
vargs = dict(translate=(-vsize[0] // 2, -vsize[1] // 2), axis_labels=["cone number", "x", "y"])
viewer = napari.view_image(np.asarray(z_slice_stack), **vargs)
viewer.axes.visible = True
napari.run()
