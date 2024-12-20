import cupy as cp
import napari
from imaging.ComptonCamera_tests.tools.compton import compton_forward
from imaging.ComptonCamera_tests.ideal.tools.seqCoinc2Cones import seqCoin2ConesArray, conesTTree2conesArray
from imaging.ComptonCamera_tests.tools.utils import remove_nans
from pathlib import Path

# Same as reco.py but combining multiple root files

##############################################################
# Settings
##############################################################
# path, E0_MeV, world_mm = Path('../sourceRectangles_cameraSingle/output/'), 0.250, 20
# path, E0_MeV, world_mm = Path('/media/billoud/Volume/CT/GATE/Gate9.2/sourceSurfaces'), 0.250, 40
# path, E0_MeV, world_mm = Path('/media/billoud/Volume/CT/GATE/Gate9.2/sourceVolumes/140keV'), 0.1405, 40
# path, E0_MeV, world_mm = Path('/media/billoud/Volume/CT/GATE/Gate9.2/sourceVolumes/140keV'), 0.140, 40
path, E0_MeV, world_mm = Path('/media/billoud/Volume/CT/GATE/ideal/sourceCube/140keV/time1000'), 0.140, 40

vsize = (256, 256, 256)
vpitch = world_mm / vsize[2]
er = 100  # inverse of cosine error
nSingles_max = 2  # maximum number of singles per coincidence, set to False to disable
true_coinc = True  # filter true coincidences (i.e. avoid singles from different events)
nentries = None

##############################################################
# Do Projection
##############################################################

######## READING sequenceCoincidence.root files ############
# fnames = list(path.rglob('CC_sequenceCoincidence.root'))
# cones = cp.concatenate([seqCoin2ConesArray(fn, E0_MeV, vsize, vpitch, er, nSingles_max, true_coinc, nentries) for fn in fnames], axis=0)
######## READING CC_Cones.root files #######################
fnames = list(path.rglob('CC_Cones.root'))
cones = cp.concatenate([conesTTree2conesArray(fn, E0_MeV, vsize, vpitch, er, nSingles_max, true_coinc, nentries) for fn in fnames], axis=0)
# ######## RECONSTRUCT #######################################
cones = remove_nans(cones)
vol = cp.zeros(vsize, dtype=cp.float32)
vol = compton_forward(vol, cones, volume_pitch=vpitch)

# ##############################################################
# # Display/Save results
# ##############################################################
vol /= vol.max()
vol = vol.get()
cp.save(fnames[0].parent.parent / "reconstruction.npy", vol)
vargs = dict(translate=(-vsize[0] // 2, -vsize[1] // 2, -vsize[2] // 2), axis_labels=["y", "x", "z"])
viewer = napari.view_image(vol, **vargs)
viewer.axes.visible = True
napari.run()
