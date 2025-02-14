# Utility functions to analyse output files
# Can be used in the main simulation script after sim.run() or offline (i.e. reading root files without simulation)
# Calling E1 the energy deposited in the Compton scattering, as in CCMod paper
import os
import sys
import numpy as np
import pandas
import uproot
import SimpleITK as sitk
import matplotlib.pyplot as plt
import cupy as cp
from pandas import Series
import imaging.ComptonCamera_tests.Gate10.tools.analysis_basics as analysis_basics
from imaging.ComptonCamera_tests.Gate10.tools.utils import *
from imaging.ComptonCamera_tests.Gate10.tools.utils import print_hits_inG4format

pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 1000)
pandas.set_option('display.float_format', lambda x: f'{x:.9}')  # G4 steps are logged with f'{x:.3}'


def singles2pixelHits(file_path, nentries=None):
    if not os.path.isfile(file_path):
        sys.exit(f"File {file_path} does not exist, probably no hit produced...")
    else:
        print(f"Converting {file_path} to pixel hits")

    singles = uproot.open(file_path)['Singles'].arrays(library='pd', entry_stop=nentries)
    print(f"{len(singles)} singles")
    pixelHits = singles[['EventID','GlobalTime', 'HitUniqueVolumeID','KineticEnergy']]
    return pixelHits

