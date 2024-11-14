import cupy as cp
import napari
from imaging.ComptonCamera_tests.tools.compton import compton_forward
from seqCoinc2ConesArray import seqCoin2ConesArray
from pathlib import Path

# Same as reco.py but combining multiple root files

##############################################################
# Settings
##############################################################
path, E0_MeV, world_mm = Path('../sourceRectangles_cameraSingle/output/'), 0.250, 20
vsize = (256, 256, 256)
vpitch = world_mm / vsize[2]
er = 100  # inverse of cosine error
nSingles_max = 2  # maximum number of singles per coincidence, set to False to disable
true_coinc = False  # filter true coincidences (i.e. avoid singles from different events)
nentries = None

##############################################################
# Do Projection
##############################################################
fnames = [sd / 'CC_sequenceCoincidence.root' for sd in path.iterdir() if sd.is_dir()]
cp_array = cp.concatenate([seqCoin2ConesArray(fn, E0_MeV, vsize, vpitch, er, nSingles_max, true_coinc, nentries) for fn in fnames], axis=0)
vol = cp.zeros(vsize, dtype=cp.float32)
vol = compton_forward(vol, cp_array, volume_pitch=vpitch)

##############################################################
# Display/Save results
##############################################################
vol = vol.get()
cp.save(fnames[0].parent / "reconstruction.npy", vol)
vargs = dict(translate=(-vsize[0] // 2, -vsize[1] // 2, -vsize[2] // 2), colormap='gray_r', axis_labels=["y", "x", "z"])
viewer = napari.view_image(vol, **vargs)
viewer.axes.visible = True
napari.run()
