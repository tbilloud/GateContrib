# Utility functions to analyse output files
# Can be used in the main simulation script after sim.run() or offline (i.e. reading root files without simulation)

import pandas
import uproot
import SimpleITK as sitk
import matplotlib.pyplot as plt
import cupy as cp
from pandas import Series
import imaging.ComptonCamera_tests.Gate10.tools.analysis_basics as analysis_basics

pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 1000)
pandas.set_option('display.float_format', lambda x: f'{x:.9f}')

def singles2cones_withDepth_byEventID(file_path):
    singles = analysis_basics.analyse_singles(file_path=file_path)
    singles_grouped = singles.groupby('EventID')
    # print(singles_grouped.size())
    cones = cp.array([])
    return cones

def singles2cones_withDepth_byGlobalTime(file_path):
    singles = analysis_basics.analyse_singles(file_path=file_path)
    # TODO: should I sort dataframe by GlobalTime?
    current_time = singles['GlobalTime'].iloc[0]
    coincident_group = []
    for single in singles.itertuples():
        if single.GlobalTime - current_time < 50:
            print(single)
    cones = cp.array([])
    return cones
