import cupy as cp
import napari
from imaging.ComptonCamera_tests.tools.compton import compton_forward
from seqCoinc2ConesTTree import seqCoinc2ConesTTree
from pathlib import Path

# Same as reco.py but combining multiple root files

path = Path('../sourceRectangles_cameraSingle/output/')
# look for every sequenceCoincidence.root file in the output directory
fnames = [sd / 'CC_sequenceCoincidence.root' for sd in path.iterdir() if sd.is_dir()]
for fn in fnames:
    print(fn)
    seqCoinc2ConesTTree(fn, fn.parent / 'CC_Cones.root')
