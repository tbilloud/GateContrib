import sys

import cupy as cp
import napari
from pathlib import Path
from imaging.ComptonCamera_tests.Gate9.tools.seqCoinc2Cones import *
from imaging.ComptonCamera_tests.tools.compton import compton_forward
from imaging.ComptonCamera_tests.tools.utils import remove_nans
from imaging.ComptonCamera_tests.Gate10.tools.utils import \
    coordinateOrigin2arrayCenter

# Script to reconstruct the source from root files with a sequenceCoincidence tree

##############################################################
# Settings
##############################################################
# fname, E0, world_z_mm = Path('../sourceRectangle_cameraSingle/output/1MBq_time1000'), 0.250, 200
# fname, E0_MeV, world_mm = Path('../sourceRectangles_cameraSingle/output'), 0.250, 20
# fname, E0_MeV, world_mm = Path('../sourceRectangles_cameraSingle/output/time100_cameraX5Y0Z9'), 0.250, 20
# fname, E0_MeV, world_mm = Path('/media/billoud/Volume/CT/GATE/Gate9/sourceSurfaces/time2000_camera_posX10_posY10'), 0.250, 40
# fname, E0_MeV, world_mm = Path('/media/billoud/Volume/CT/GATE/Gate9/sourceVolumes/140keV/time200_camera_posX0_posY0'), 0.1405, 40
# fname, E0_MeV, world_mm = Path('/media/billoud/Volume/CT/GATE/Gate9/sourceVolumes/245keV/time200_camera_posX0_posY0'), 0.245, 40
# fname, E0_MeV, world_mm = Path('/media/billoud/Volume/CT/GATE/Gate9/sourceCube/140keV/time1000/time1000_seed1_cameraX0Y0Z10'), 0.140, 40
fname, E0_MeV, world_mm = Path('../output'), 0.140, 200

vsize = (256, 256, 256)
vpitch = world_mm / vsize[2]
er = 100  # inverse of cosine error
nSingles_max = 2  # maximum number of singles per coincidence, set to False to disable
true_coinc = True  # filter true coincidences (i.e. avoid singles from different events)
nentries = None  # None to read all entries

##############################################################
# Do Projection
##############################################################

# ###### READING sequenceCoincidence.root files ##############
cones = seqCoin2ConesArray(fname / 'CC_sequenceCoincidence.root', E0_MeV, vsize, vpitch, er, nSingles_max, true_coinc, nentries)
# ###### READING CC_Cones.root files #########################
# cones = conesTTree2conesArray(fname / 'CC_Cones.root', E0_MeV, vsize, vpitch, er, nSingles_max, true_coinc, nentries)

# ######## RECONSTRUCT #######################################
cones = remove_nans(cones)
cones = coordinateOrigin2arrayCenter(cones, vpitch, vsize)
vol = cp.zeros(vsize, dtype=cp.float32)
vol = compton_forward(vol, cones, volume_pitch=vpitch)

##############################################################
# Display/Save results
##############################################################
vol /= vol.max()
vol = vol.get()
cp.save(fname / "reconstruction.npy", vol)
vargs = dict(translate=(-vsize[0] // 2, -vsize[1] // 2, -vsize[2] // 2), axis_labels=["y", "x", "z"], colormap='gray_r')
viewer = napari.view_image(vol, **vargs)
viewer.axes.visible = True
# TODO: add cuboid representing th detector (see napari's bounding box / annotation plugin?)
napari.run()
