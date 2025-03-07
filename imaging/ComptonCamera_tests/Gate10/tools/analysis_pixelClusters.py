# Functions to process pixelClusters dataframes
import sys
import time

from tools.analysis_pixelHits import *
import pandas as pd
from opengate.logger import global_log

pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 1000)
pandas.set_option('display.float_format', lambda x: f'{x:.9}')  # G4 steps are logged with f'{x:.3}'

pixelClusters_columns = ['PixelID', TOA, ENERGY]

# TODO: if source.n was used in simulation, clustering with TOA does not work
#  -> detect it ? send warning?
import pandas as pd

def new_cluster(clusters_list, cluster_df, hit):
    clusters_list.append(process_cluster_inputDF_outputDF(cluster_df))
    new_cluster_df = pd.DataFrame([hit])
    new_time_window_start = hit[TOA]
    return new_cluster_df, new_time_window_start

# TODO speed -> https://pandas.pydata.org/docs/user_guide/basics.html#iteration
def pixelHits2cones(pixelHits_df, n_pixels, time_window_ns=100):
    global_log.info(f'Running cluster analysis, {len(pixelHits_df)} pixel hits')

    pixelHits_df = pixelHits_df.sort_values(by='ToA_ns')

    start_time = time.time()
    clusters = []
    cluster = pd.DataFrame()  # Initialize as an empty DataFrame
    window_start = None

    for index, hit in pixelHits_df.iterrows():
        if cluster.empty:
            cluster = pd.concat([cluster, hit.to_frame().T], ignore_index=True)
            window_start = hit[TOA]
        else:
            if hit[TOA] - window_start <= time_window_ns:
                if is_adjacent(hit, cluster, n_pixels):
                    cluster = pd.concat([cluster, hit.to_frame().T], ignore_index=True)
                else:
                    cluster, window_start = new_cluster(clusters, cluster, hit)
            else:
                cluster, window_start = new_cluster(clusters, cluster, hit)

    # Add the last cluster
    if not cluster.empty:
        clusters.append(process_cluster_inputDF_outputDF(cluster))

    # Convert clusters to DataFrame
    pixelClusters_df = pd.concat(clusters, ignore_index=True)

    print('Number of clusters:', len(pixelClusters_df))
    print('Clustering time:', round(time.time() - start_time), 'seconds')
    return pixelClusters_df

def is_adjacent(hit, current_cluster_df, n_pixels):
    x1, y1 = get_pixID_2D(hit[PIXEL_ID], n_pixels)
    return any(
        abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1
        for x2, y2 in
        (get_pixID_2D(cluster_hit[PIXEL_ID], n_pixels) for _, cluster_hit in current_cluster_df.iterrows())
    )

def process_cluster_inputDF_outputDF(cluster_df):
    cluster_total_energy = cluster_df[ENERGY].sum()
    cluster_first_TOA = cluster_df[TOA].min()
    return pd.DataFrame({
        'ClusterTotalEnergy': [cluster_total_energy],
        'ClusterFirstTOA': [cluster_first_TOA]
    })