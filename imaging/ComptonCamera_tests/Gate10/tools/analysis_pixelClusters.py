# Functions to process pixelClusters dataframes
import time

from imaging.ComptonCamera_tests.Gate10.tools.analysis_pixelHits import *
import pandas as pd

pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 1000)
pandas.set_option('display.float_format', lambda x: f'{x:.9}')  # G4 steps are logged with f'{x:.3}'

pixelClusters_columns = ['PixelID', TOA, ENERGY]

# TODO: if source.n was used in simulation, clustering with TOA does not work
#  -> detect it ? send warning?
def pixelHits2pixelClusters(pixelHits_df, n_pixels, time_window_ns=100):

    pixelHits_df = pixelHits_df.sort_values(by='ToA_ns') # TODO: necessary?

    start_time = time.time()
    clusters_list = []
    current_cluster_df = pd.DataFrame()  # Initialize as an empty DataFrame
    current_time_window_start = None

    for index, hit in pixelHits_df.iterrows():
        if current_cluster_df.empty:
            # Start a new cluster
            # print('Starting a new cluster')
            current_cluster_df = pd.concat([current_cluster_df, hit.to_frame().T], ignore_index=True)
            current_time_window_start = hit[TOA]
        else:
            # Check if the hit is within the time window
            if hit[TOA] - current_time_window_start <= time_window_ns:
                # print('Adding hit to current cluster')
                if is_adjacent(hit, current_cluster_df, n_pixels):
                    current_cluster_df = pd.concat([current_cluster_df, hit.to_frame().T], ignore_index=True)
                else:
                    # Save the current cluster and start a new one
                    clusters_list.append(process_cluster_inputDF_outputDF(current_cluster_df))
                    current_cluster_df = pd.DataFrame([hit])
                    current_time_window_start = hit[TOA]
            else:
                # Save the current cluster and start a new one
                # print('Saving current cluster and starting a new one')
                clusters_list.append(process_cluster_inputDF_outputDF(current_cluster_df))
                current_cluster_df = pd.DataFrame([hit])
                current_time_window_start = hit[TOA]

    # Add the last cluster
    if not current_cluster_df.empty:
        # print('Adding last cluster')
        clusters_list.append(process_cluster_inputDF_outputDF(current_cluster_df))

    # Convert clusters to DataFrame
    pixelClusters_df = pd.concat(clusters_list, ignore_index=True)

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