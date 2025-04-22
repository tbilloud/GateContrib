# Functions to process pixelClusters dataframes

import analysis_pixelHits
from tools.analysis_pixelHits import *
from opengate.logger import global_log
import pandas as pd

pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 400)
pd.set_option('display.max_rows', 1000)
pd.set_option('display.float_format', lambda x: f'{x:.9}')  # G4 steps are logged with f'{x:.3}'

PIXEL_ID = 'PixelID_int16'
ENERGY = 'Energy_keV'
TOA = 'TOA_ns'
pixelClusters_columns = [PIXEL_ID, TOA, ENERGY]
EVENTID = 'EventID'
X_um = 'PositionX'
Y_um = 'PositionY'
simulation_columns = [EVENTID, X_um, Y_um]

# TODO: if source.n was used in simulation, clustering with TOA does not work
#  -> detect it ? send warning?

def is_adjacent(hit, current_cluster_df, n_pixels):
    x1, y1 = get_pixID_2D(hit[PIXEL_ID], n_pixels)
    return any(
        abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1
        for x2, y2 in
        (get_pixID_2D(cluster_hit[PIXEL_ID], n_pixels) for _, cluster_hit in current_cluster_df.iterrows())
    )

def process_cluster_method1(cluster_df):
    cluster_total_energy = cluster_df[analysis_pixelHits.ENERGY_keV].sum()
    cluster_first_TOA = cluster_df[analysis_pixelHits.TOA].min()
    cluster_first_eventID = int(cluster_df[analysis_pixelHits.EVENTID].min())
    return pd.DataFrame({
        ENERGY_keV: [cluster_total_energy],
        TOA: [cluster_first_TOA],
        EVENTID: [cluster_first_eventID]
    })

def process_cluster_method2(cluster_df, n_pixels, pixel_pitch_um, thickness_um):
    cluster_total_energy = cluster_df[analysis_pixelHits.ENERGY_keV].sum()
    cluster_first_TOA = cluster_df[analysis_pixelHits.TOA].min()
    cluster_first_eventID = int(cluster_df[analysis_pixelHits.EVENTID].min())
    pixX, pixY = zip(*cluster_df[PIXEL_ID].apply(get_pixID_2D, args=(n_pixels,)))
    x_um = pixel_pitch_um * sum(pixX * cluster_df[analysis_pixelHits.ENERGY_keV]) / cluster_total_energy
    y_um = pixel_pitch_um * sum(pixY * cluster_df[analysis_pixelHits.ENERGY_keV]) / cluster_total_energy
    return pd.DataFrame({
        ENERGY_keV: [cluster_total_energy],
        TOA: [cluster_first_TOA],
        EVENTID: [cluster_first_eventID],
        X_um: [x_um],
        Y_um: [y_um],
    })

process_cluster_functions = {
    'method1': process_cluster_method1,
    'method2': process_cluster_method2
}

def new_cluster(clusters_list, cluster_df, hit, n_pixels, process_cluster_func, **kwargs):
    process_func = process_cluster_functions[process_cluster_func]
    clusters_list.append(process_func(cluster_df, n_pixels, **kwargs))
    new_cluster_df = pd.DataFrame([hit])
    new_time_window_start = hit[analysis_pixelHits.TOA]
    return new_cluster_df, new_time_window_start

# TODO speed -> https://pandas.pydata.org/docs/user_guide/basics.html#iteration
def pixelHits2pixelClusters(pixelHits, n_pixels, time_window_ns,
                            cluster_func, **kwargs):
    global_log.info(f"Offline: pixel cluster analysis with pixel hit df input")

    pixelHits = pixelHits.sort_values(by=analysis_pixelHits.TOA)

    # 1st cluster & initialization
    cluster = pd.DataFrame([pixelHits.iloc[0]])  # Initialize with the first hit
    window_start = pixelHits.iloc[0][analysis_pixelHits.TOA]
    clusters = []

    # Loop over hits
    for index, hit in pixelHits.iterrows():
        if hit[analysis_pixelHits.TOA] - window_start <= time_window_ns and is_adjacent(hit, cluster, n_pixels):
            cluster = pd.concat([cluster, hit.to_frame().T], ignore_index=True)
        else:
            cluster, window_start = new_cluster(clusters, cluster, hit, n_pixels, cluster_func, **kwargs)

    # Last cluster
    new_cluster(clusters, cluster, hit, n_pixels, cluster_func, **kwargs)

    global_log.debug(f"Number of clusters: {len(clusters)}")
    return pd.concat(clusters, ignore_index=True)

