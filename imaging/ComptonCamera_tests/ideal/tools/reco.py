import cupy as cp
import napari
from pathlib import Path
from seqCoinc2ConesArray import seqCoin2ConesArray as cones
from imaging.ComptonCamera_tests.tools.compton import compton_forward

# Script to reconstruct the source from root files with a sequenceCoincidence tree

##############################################################
# Settings
##############################################################
#fname, E0, world_z_mm = Path('../sourceRectangle_cameraSingle/output/1MBq_time1000'), 0.250, 200
fname, E0_MeV, world_mm = Path('../sourceRectangles_cameraSingle/output'), 0.250, 20

vsize = (256, 256, 256)
vpitch = world_mm / vsize[2]
er = 100  # inverse of cosine error
nSingles_max = 2  # maximum number of singles per coincidence, set to False to disable
true_coinc = False  # filter true coincidences (i.e. avoid singles from different events)
nentries = None

##############################################################
# Do Projection
##############################################################
array = cones(fname / 'CC_sequenceCoincidence.root', E0_MeV, vsize, vpitch, er, nSingles_max, true_coinc, nentries)
vol = cp.zeros(vsize, dtype=cp.float32)
vol = compton_forward(vol, array, volume_pitch=vpitch)

##############################################################
# Display/Save results
##############################################################
vol = vol.get()
cp.save(fname.parent / "reconstruction.npy", vol)
viewer = napari.view_image(vol, translate=(-vsize[0] // 2, -vsize[1] // 2, -vsize[2] // 2), colormap='gray_r',
                           axis_labels=["y", "x", "z"])
viewer.axes.visible = True
napari.run()