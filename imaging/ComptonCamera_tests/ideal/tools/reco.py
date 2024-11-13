import cupy as cp
import napari
from seqCoinc2ConesArray_ideal import seqCoin2Cones
from imaging.ComptonCamera_tests.tools.compton import compton_forward

# Script to reconstruct the source from root files with a sequenceCoincidence tree

##############################################################
# Settings
##############################################################
# fname, E0 = '../point_source/output/camera_X0Y40Z48/CC_sequenceCoincidence.root', 0.250
fname, E0 = '../cameraSingle/output/CC_sequenceCoincidence.root', 0.250
vsize = (256, 256, 256)
vpitch = 1
inv_cos_error = 100

##############################################################
# Do Projection
##############################################################
cp_array = seqCoin2Cones(fname, E0, vsize, vpitch, inv_cos_error, nSingles_max=2, filter_TrueCoinc=False)
vol = cp.zeros(vsize, dtype=cp.float32)
vol = compton_forward(vol, cp_array, volume_pitch=vpitch)

##############################################################
# Display/Save results
##############################################################
vol = vol.get()
# cp.save("vol.npy", vol)
viewer = napari.view_image(vol, translate=(-vsize[0] // 2, -vsize[1] // 2, -vsize[2] // 2), colormap='gray_r',
                           axis_labels=["y", "x", "z"])
viewer.axes.visible = True
napari.run()
