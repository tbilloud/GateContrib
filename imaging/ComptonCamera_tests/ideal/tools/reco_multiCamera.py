import os
import cupy as cp
import napari
from imaging.ComptonCamera_tests.tools.compton import compton_forward
from seqCoinc2ConesArray import seqCoin2ConesArray
from pathlib import Path

# Same as reco.py but combining multiple root files

##############################################################
# Settings
##############################################################
path = Path('../sourcePoint_cameraDouble/output/')
E0 = 0.250  # MeV, incident gamma energy (adapt to energy_cut)
vsize = (256, 256, 256)
vpitch = 1
er = 100  # inverse of cosine error
nSingles_max = 2  # maximum number of singles per coincidence, set to False to disable
true_coinc = False  # filter true coincidences (i.e. avoid singles from different events)
nentries = None

##############################################################
# Do Projection
##############################################################
fnames = [sd / 'CC_sequenceCoincidence.root' for sd in path.iterdir() if sd.is_dir()]
cp_array = cp.concatenate([seqCoin2ConesArray(fn, E0, vsize, vpitch, er, nSingles_max, true_coinc, nentries) for fn in fnames], axis=0)
vol = cp.zeros(vsize, dtype=cp.float32)
vol = compton_forward(vol, cp_array, volume_pitch=vpitch)

##############################################################
# Display/Save results
##############################################################
vol = vol.get()
cp.save(fnames[0].parent / "reconstruction.npy", vol)
viewer = napari.view_image(vol, translate=(-vsize[0] // 2, -vsize[1] // 2, -vsize[2] // 2), colormap='gray_r',
                           axis_labels=["y", "x", "z"])
viewer.axes.visible = True
napari.run()
