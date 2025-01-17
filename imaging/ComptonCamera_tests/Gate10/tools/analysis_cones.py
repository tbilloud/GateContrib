# Utility functions to analyse output files
# Can be used in the main simulation script after sim.run() or offline (i.e. reading root files without simulation)
import sys

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

# Compton scattering hits/steps can be identified with:
# 1) ProcessDefinedStep = compt
# 2) TrackCreatorProcess = compt in which case the parent track had a ProcessDefinedStep = Transportation
# TODO: understand case 2 !
def extract_ideal_hits(file_path):
    hits = analysis_basics.analyse_hits(file_path=file_path)
    print(f"{hits['EventID'].nunique()} events interacted in the sensor")

    print(hits[hits['EventID'] == 487].sort_values(by='TrackID').to_string(index=False)), sys.exit()

    print(hits[hits['ProcessDefinedStep'] == 'compt'].to_string(index=False))
    print(hits[hits['TrackCreatorProcess'] == 'compt'].to_string(index=False))


def hits2cones_withDepth_byEventID(file_path):
    hits = analysis_basics.analyse_hits(file_path=file_path)
    print(f"{hits['EventID'].nunique()} events interacted in the sensor")

    # print(hits[hits['EventID'] == 0].sort_values(by='TrackID').to_string(index=False))# , sys.exit()

    grouped = hits.groupby('EventID')
    # print(grouped.size())

    # energy_deposit_sums = grouped['TotalEnergyDeposit'].sum()
    # for event_id, total_deposit in energy_deposit_sums.items():
    #     print(f"EventID: {event_id}, TotalEnergyDeposit: {total_deposit}")
    # print('\n')

    filtered_event_ids = [eventid for eventid, group in grouped if 'compt' in group['TrackCreatorProcess'].tolist()]
    filtered_df = hits[hits['EventID'].isin(filtered_event_ids)]
    print(f"{filtered_df['EventID'].nunique()} events with at least one compton interaction")

    compt_hits = hits[hits['TrackCreatorProcess'] == 'compt']
    compton_counts = compt_hits.groupby('EventID').size()
    print(f"{(compton_counts == 1).sum()} events with exactly one compton interaction")

    # energy_deposit_sums2 = filtered_df.groupby('EventID')['TotalEnergyDeposit'].sum()
    # for event_id, total_deposit in energy_deposit_sums2.items():
    #     print(f"EventID: {event_id}, TotalEnergyDeposit: {total_deposit}")


def singles2cones_withDepth_byEventID(file_path):
    singles = analysis_basics.analyse_singles(file_path=file_path)
    print(singles)
    singles_grouped = singles.groupby('EventID')
    print(singles_grouped.size())
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
