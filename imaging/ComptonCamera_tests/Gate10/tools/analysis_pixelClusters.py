# Functions to process pixelClusters dataframes

from tools.analysis_pixelHits import *
from opengate.logger import global_log
from analysis_pixelHits import PIXEL_ID, TOA, ENERGY_keV, EVENTID
import pandas as pd

pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 400)
pd.set_option('display.max_rows', 1000)
pd.set_option('display.float_format',
              lambda x: f'{x:.9}')  # G4 steps are logged with f'{x:.3}'

pixelClusters_columns = [PIXEL_ID, TOA, ENERGY_keV]  # TODO not used
X_um = 'PositionX'
Y_um = 'PositionY'
simulation_columns = [EVENTID, X_um, Y_um]  # TODO not used


# TODO: if source.n was used in simulation, clustering with TOA does not work
#  -> detect it ? send warning?

def is_adjacent(hit, cluster, n_pix):
    x1, y1 = get_pixID_2D(hit[PIXEL_ID], n_pix)
    return any(
        abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1
        for x2, y2 in
        (get_pixID_2D(hit[PIXEL_ID], n_pix) for _, hit in cluster.iterrows())
    )


def process_cluster_method1(cluster_df):
    cluster_total_energy = cluster_df[ENERGY_keV].sum()
    cluster_first_TOA = cluster_df[TOA].min()
    cluster_first_eventID = int(cluster_df[EVENTID].min())
    return pd.DataFrame({
        ENERGY_keV: [cluster_total_energy],
        TOA: [cluster_first_TOA],
        EVENTID: [cluster_first_eventID]
    })


def process_cluster_method2(cluster, n_pixels, pitch_um):
    cluster_total_energy = cluster[ENERGY_keV].sum()
    cluster_first_TOA = cluster[TOA].min()
    cluster_first_eventID = int(cluster[EVENTID].min())
    pixX, pixY = zip(*cluster[PIXEL_ID].apply(get_pixID_2D, args=(n_pixels,)))
    x_um = pitch_um * sum(pixX * cluster[ENERGY_keV]) / cluster_total_energy
    y_um = pitch_um * sum(pixY * cluster[ENERGY_keV]) / cluster_total_energy
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


def new_clust(clust_list, cluster, hit, n_pixels, process_func, **kwargs):
    process_func = process_cluster_functions[process_func]
    clust_list.append(process_func(cluster, n_pixels, **kwargs))
    new_cluster_df = pd.DataFrame([hit])
    new_time_window_start = hit[TOA]
    return new_cluster_df, new_time_window_start


# TODO speed -> https://pandas.pydata.org/docs/user_guide/basics.html#iteration
def pixelHits2pixelClusters(pixelHits, npix, window_ns, func, **kwargs):
    global_log.info(f"Offline [pixelClusters]: START")
    global_log.debug(f"Input pixel hits dataframe")
    stime = time.time()

    pixelHits = pixelHits.sort_values(by=TOA)

    # 1st cluster & initialization
    clust = pd.DataFrame([pixelHits.iloc[0]])  # Initialize with first hit
    wst = pixelHits.iloc[0][TOA] # window start
    clusters = []

    # Loop over hits
    for index, hit in pixelHits.iterrows():
        if hit[TOA] - wst <= window_ns and is_adjacent(hit, clust, npix):
            clust = pd.concat([clust, hit.to_frame().T], ignore_index=True)
        else:
            clust, wst = new_clust(clusters, clust, hit, npix, func, **kwargs)

    # Last cluster
    new_clust(clusters, clust, hit, npix, func, **kwargs)

    global_log.debug(f"{len(clusters)} clusters")
    global_log.info(f"Offline [pixelClusters]: STOP. Time: {time.time() - stime:.1f} seconds.\n" + '-' * 80)
    return pd.concat(clusters, ignore_index=True)
