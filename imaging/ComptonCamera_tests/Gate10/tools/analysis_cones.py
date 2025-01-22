# Utility functions to analyse output files
# Can be used in the main simulation script after sim.run() or offline (i.e. reading root files without simulation)
# Calling E1 the energy deposited in the Compton scattering, as in CCMod paper

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


def extract_ideal_hits_byEventID(file_path, source_energy_MeV):
    hits = uproot.open(file_path)['Hits'].arrays(library='pd', entry_stop=None)  # None to read all entries
    # print(hits)
    print(f"{hits['EventID'].nunique()} events interacted in the sensor")

    grouped = hits.groupby('EventID')

    # Filter events with at least one compton interaction
    # TODO: in the 1st track? (to avoid gammas coming from e.g. compton interaction in air or surrounding volumes)
    filtered_event_ids = [eventid for eventid, group in grouped if 'compt' in group['ProcessDefinedStep'].tolist()]
    filtered_df = hits[hits['EventID'].isin(filtered_event_ids)]
    print(f"{filtered_df['EventID'].nunique()} events with at least one compton interaction")
    # print(filtered_df.to_string(index=False))

    # # Filter events with exactly one compton interaction
    # compt_hits = hits[hits['ProcessDefinedStep'] == 'compt']
    # compton_counts = compt_hits.groupby('EventID').size()
    # for i in range(1, compton_counts.max() + 1):
    #     print(f"{(compton_counts == i).sum()} events with exactly {i} compton interaction{'s' if i > 1 else ''}")
    # single_compton_event_ids = compton_counts[compton_counts == 1].index
    # filtered_df = filtered_df[filtered_df['EventID'].isin(single_compton_event_ids)]
    # # print(filtered_df.to_string(index=False))

    # Filter events where sum of energy deposits matches source energy
    energy_deposit_sums = filtered_df.groupby('EventID')['TotalEnergyDeposit'].sum()
    # for event_id, total_deposit in energy_deposit_sums.items():
    #     print(f"EventID: {event_id}, TotalEnergyDeposit: {total_deposit}")
    filtered_event_ids = energy_deposit_sums[energy_deposit_sums == source_energy_MeV].index
    filtered_df = filtered_df[filtered_df['EventID'].isin(filtered_event_ids)]

    return filtered_df

# TODO: I need one version writing array for direct reco and one with extra simu info for validation?
def hits2cones_withDepth_byEventID(file_path, source_energy_MeV, nentries = None, store_info=False):
    # ideal_hits = extract_ideal_hits_byEventID(file_path=file_path, source_energy_MeV=source_energy_MeV)

    # TODO Deal with different cases
    # TODO For now I only care about compton interactions from primary gamma (i.e. TrackID == 1) with full energy
    #  deposited in sensor
    # 1) if 1st track starts with Transportation, recoil e- was not tracked
    #   a) 2nd hit in 1st track is compt, E1 is in TotalEnergyDeposit of 1st row
    #   b) 2nd hit in 1st track is none, TODO ???
    # 2) if 1st track starts with compt, recoil e- was tracked
    hits = uproot.open(file_path)['Hits'].arrays(library='pd', entry_stop=nentries)  # None to read all entries
    print(hits.to_string(index=False))
    grouped = hits.groupby('EventID')
    cones = []
    for eventid, group in grouped:
        first_row = group.iloc[0]
        if first_row['TrackID'] == 1:
            if group['TotalEnergyDeposit'].sum() == source_energy_MeV:
                first_process = first_row['ProcessDefinedStep']
                if first_process == 'compt':
                    print(eventid, 'recoil e- was tracked')
                elif first_process == 'Transportation':

                    print(eventid, 'recoil e- was not tracked')
                    apex = [first_row['PostPosition_X'], first_row['PostPosition_Y'], first_row['PostPosition_Z']]
                    normalized_direction = [-first_row['PostDirection_X'], -first_row['PostDirection_Y'], -first_row['PostDirection_Z']]
                    cosT = 1 - (0.511 * first_row['TotalEnergyDeposit']) / (source_energy_MeV * (source_energy_MeV - first_row['TotalEnergyDeposit']))
                    cone = apex + normalized_direction + [cosT] + [200]
                    cones.append(cone + [eventid] if store_info else cone)
                else:
                    print('*' * 100)
        else:
            print('event not from gamma source')
    cones = cp.array(cones)
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
