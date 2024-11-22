import sys

import cupy as cp
import napari
from pathlib import Path

import numpy as np

from imaging.ComptonCamera_tests.ideal.tools.seqCoinc2Cones import *
from imaging.ComptonCamera_tests.tools.compton import compton_forward
from imaging.ComptonCamera_tests.tools.utils import remove_nans

# Script to check the precision of ideal simulation with point source
# All cones should intersect at the source point

##############################################################
# Settings
##############################################################
fname, E0_MeV, world_mm = Path('../sourcePoint_cameraSingle/output'), 0.100, 200

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
plane = list()
for cone in cones:
    vol = cp.zeros(vsize, dtype=cp.float32)
    print(cone)
    vol = compton_forward(vol, cone, volume_pitch=vpitch)
    plane.append(vol[:, :, 0].get())

# print(np.asarray(plane).shape), sys.exit()

##############################################################
# Display/Save results
##############################################################
vargs = dict(translate=(-vsize[0] // 2, -vsize[1] // 2), axis_labels=["cone number", "x", "y"])
viewer = napari.view_image(np.asarray(plane), **vargs)
viewer.axes.visible = True
napari.run()
