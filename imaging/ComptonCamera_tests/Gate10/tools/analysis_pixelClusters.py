# Functions to process pixelClusters dataframes

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

pixelClusters_columns = ['PixelID', 'ToA', 'Energy']

import pandas as pd
import numpy as np


def pixelHits2pixelClusters(pixelHits_df, time_window_ns=100):

    # TODO: necessary?
    pixelHits_df = pixelHits_df.sort_values(by='ToA')

    clusters = []
    current_cluster = []
    current_time_window_start = None

    for index, hit in pixelHits_df.iterrows():
        if not current_cluster:
            # Start a new cluster
            current_cluster.append(hit)
            current_time_window_start = hit['ToA']
        else:
            # Check if the hit is within the time window
            if hit['ToA'] - current_time_window_start <= time_window_ns:
                # Check if the hit is adjacent to any hit in the current cluster
                is_adjacent = any(
                    abs(hit['PixelID'] - cluster_hit['PixelID']) == 1
                    for cluster_hit in current_cluster
                )
                if is_adjacent:
                    current_cluster.append(hit)
                else:
                    # Save the current cluster and start a new one
                    clusters.append(current_cluster)
                    current_cluster = [hit]
                    current_time_window_start = hit['ToA']
            else:
                # Save the current cluster and start a new one
                clusters.append(current_cluster)
                current_cluster = [hit]
                current_time_window_start = hit['ToA']

    # Add the last cluster
    if current_cluster:
        clusters.append(current_cluster)

    # Convert clusters to DataFrame
    cluster_dfs = [pd.DataFrame(cluster) for cluster in clusters]
    pixelClusters_df = pd.concat(cluster_dfs, ignore_index=True)

    return pixelClusters_df