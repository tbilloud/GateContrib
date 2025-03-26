# Functions to process pixelClusters dataframes

import time

import analysis_pixelHits
from tools.analysis_pixelHits import *
from opengate.logger import global_log
import pandas as pd

pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 1000)
pandas.set_option('display.float_format', lambda x: f'{x:.9}')  # G4 steps are logged with f'{x:.3}'

PIXEL_ID = 'PixelID_int16'
ENERGY = 'ClusterTotalEnergy'
TOA = 'ClusterFirstTOA'
pixelClusters_columns = [PIXEL_ID, TOA, ENERGY]
EVENTID = 'EventID'
POSITION_X = 'PositionX'
POSITION_Y = 'PositionY'
POSITION_Z = 'PositionZ'
simulation_columns = [EVENTID, POSITION_X, POSITION_Y, POSITION_Z]

# TODO: if source.n was used in simulation, clustering with TOA does not work
#  -> detect it ? send warning?

def is_adjacent(hit, current_cluster_df, n_pixels):
    x1, y1 = get_pixID_2D(hit[PIXEL_ID], n_pixels)
    return any(
        abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1
        for x2, y2 in
        (get_pixID_2D(cluster_hit[PIXEL_ID], n_pixels) for _, cluster_hit in current_cluster_df.iterrows())
    )

def process_cluster(cluster_df):
    cluster_total_energy = cluster_df[analysis_pixelHits.ENERGY].sum()
    cluster_first_TOA = cluster_df[analysis_pixelHits.TOA].min()
    cluster_first_eventID = int(cluster_df[analysis_pixelHits.EVENTID].min())
    return pd.DataFrame({
        ENERGY: [cluster_total_energy],
        TOA: [cluster_first_TOA],
        EVENTID: [cluster_first_eventID]
    })

def new_cluster(clusters_list, cluster_df, hit):
    clusters_list.append(process_cluster(cluster_df))
    new_cluster_df = pd.DataFrame([hit])
    new_time_window_start = hit[analysis_pixelHits.TOA]
    return new_cluster_df, new_time_window_start

# TODO speed -> https://pandas.pydata.org/docs/user_guide/basics.html#iteration
def pixelHits2pixelClusters(pixelHits, n_pixels, time_window_ns=100):
    global_log.info(f"Offline: cluster analysis with dataframe input")

    pixelHits = pixelHits.sort_values(by='ToA_ns')

    # 1st cluster & initialization
    cluster = pd.DataFrame([pixelHits.iloc[0]])  # Initialize with the first hit
    window_start = pixelHits.iloc[0][analysis_pixelHits.TOA]
    clusters = []

    # Loop over hits
    for index, hit in pixelHits.iterrows():
        if hit[analysis_pixelHits.TOA] - window_start <= time_window_ns:
            if is_adjacent(hit, cluster, n_pixels): # update cluster
                cluster = pd.concat([cluster, hit.to_frame().T], ignore_index=True)
            else: # new cluster
                cluster, window_start = new_cluster(clusters, cluster, hit)
        else: # new cluster
            cluster, window_start = new_cluster(clusters, cluster, hit)

    # Last cluster
    if not cluster.empty:
        clusters.append(process_cluster(cluster))

    # Convert clusters to DataFrame
    pixelClusters_df = pd.concat(clusters, ignore_index=True)

    global_log.debug(f"Number of clusters: {len(pixelClusters_df)}")
    return pixelClusters_df

