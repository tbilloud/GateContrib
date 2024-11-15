from imaging.ComptonCamera_tests.ideal.tools.seqCoinc2Cones import seqCoinc2ConesTTree
from pathlib import Path

# When reconstructing large files (> 1M cones), better to save cone TTrees rather than reading sequenceCoincidence.root

path = Path('../sourceRectangles_cameraSingle/output/')
fnames = list(path.rglob('CC_sequenceCoincidence.root'))
for fn in fnames:
    seqCoinc2ConesTTree(fn, fn.parent / 'CC_Cones.root')
