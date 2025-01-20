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


def extract_ideal_hits(file_path, source_energy_MeV):
    hits = uproot.open(file_path)['Hits'].arrays(library='pd', entry_stop=None)  # None to read all entries

    print(f"{hits['EventID'].nunique()} events interacted in the sensor")

    grouped = hits.groupby('EventID')

    # Filter events with at least one compton interaction
    filtered_event_ids = [eventid for eventid, group in grouped if 'compt' in group['ProcessDefinedStep'].tolist()]
    filtered_df = hits[hits['EventID'].isin(filtered_event_ids)]
    print(f"{filtered_df['EventID'].nunique()} events with at least one compton interaction")
    # print(filtered_df.to_string(index=False))

    # Filter events with exactly one compton interaction
    compt_hits = hits[hits['ProcessDefinedStep'] == 'compt']
    compton_counts = compt_hits.groupby('EventID').size()
    for i in range(1, compton_counts.max() + 1):
        print(f"{(compton_counts == i).sum()} events with exactly {i} compton interaction{'s' if i > 1 else ''}")
    single_compton_event_ids = compton_counts[compton_counts == 1].index
    filtered_df = filtered_df[filtered_df['EventID'].isin(single_compton_event_ids)]
    # print(filtered_df.to_string(index=False))

    # Filter events where sum of energy deposits matches source energy
    energy_deposit_sums = filtered_df.groupby('EventID')['TotalEnergyDeposit'].sum()
    # for event_id, total_deposit in energy_deposit_sums.items():
    #     print(f"EventID: {event_id}, TotalEnergyDeposit: {total_deposit}")
    filtered_event_ids = energy_deposit_sums[energy_deposit_sums == source_energy_MeV].index
    filtered_df = filtered_df[filtered_df['EventID'].isin(filtered_event_ids)]

    return filtered_df


def hits2cones_withDepth_byEventID(file_path, source_energy_MeV):
    ideal_hits = extract_ideal_hits(file_path=file_path, source_energy_MeV=source_energy_MeV)
    print(ideal_hits.to_string(index=False))

    # TODO
    # deal with tracks where recoil was tracked and those where it was not

    cones = cp.array([])
    return cones


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
