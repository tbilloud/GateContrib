# Utility functions to analyse output files
# Can be used in the main simulation script after sim.run() or offline (i.e. reading root files without simulation)
# Calling E1 the energy deposited in the Compton scattering, as in CCMod paper
import os
import sys
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


# # TODO: I need one version writing array for direct reco and one with extra simu info for validation?
# def hits2cones_byEventID(file_path, source_MeV, nentries=None, store_info=False):
#     if not os.path.isfile(file_path):
#         sys.exit(f"File {file_path} does not exist, probably no hit produced...")
#     hits = uproot.open(file_path)['Hits'].arrays(library='pd', entry_stop=nentries)  # None to read all entries
#     utils.print_hits_short(hits)  # , sys.exit()
#     n_events = hits['EventID'].nunique()
#     print(f"{n_events} events interacted in the sensor")
#     grouped = hits.groupby('EventID')
#     cones = []
#
#     # For now I only care about compton interactions from primary gamma with full energy deposited in sensor
#     # TODO: deal with
#     #   doppler
#     #   PIXE/fluo
#     n_events_secondary, n_events_photoelectric, n_events_recoil_tracked, n_events_recoil_not_tracked = 0, 0, 0, 0
#     n_events_escape_a, n_events_escape_b = 0, 0
#     n_events_primary = 0
#     n_events_full_energy_deposit = 0
#     for eventid, group in grouped:
#         row1 = group.iloc[0]
#         apex, direction, E1 = False, False, False
#         # Sensor received primary gamma
#         if row1['ParentParticleName'] == 'unknown': # TODO: is this correct with radioisotope source?
#             # All primary energy was deposited
#             # else: subcases differs! e.g. photon escapes after Compton and recoil e- tracked => photon track not stored
#             if round(group['TotalEnergyDeposit'].sum(),6) == source_MeV: # round to avoid float precision issues
#                 first_process = row1['ProcessDefinedStep']
#                 energy_dep = group[group['ParentID'] == 1]['TotalEnergyDeposit'].sum()
#                 kinetic_energy_sum = group[group['ParentID'] == 1]['KineticEnergy'].iloc[0].sum()
#                 print(energy_dep, kinetic_energy_sum)
#                 # Compton interaction, recoil e- tracked
#                 if first_process == 'compt':
#                     # print(group['TrackID'].value_counts())
#                     # print(group['TrackID'].nunique())
#                     apex = [row1['PrePosition_X'], row1['PrePosition_Y'], row1['PrePosition_Z']]
#                     direction = [-row1['PreDirection_X'], -row1['PreDirection_Y'], -row1['PreDirection_Z']]
#                     E1 = source_MeV - row1['KineticEnergy']
#                     n_events_recoil_tracked += 1
#                 # Several possible cases
#                 elif first_process == 'Transportation':
#                     # Photo-electric absorption
#                     if group['TrackID'].value_counts()[1] == 1:
#                         n_events_photoelectric += 1
#                     # Compton interaction, recoil e- not tracked
#                     else:
#                         apex = [row1['PostPosition_X'], row1['PostPosition_Y'], row1['PostPosition_Z']]
#                         direction = [-row1['PostDirection_X'], -row1['PostDirection_Y'], -row1['PostDirection_Z']]
#                         E1 = row1['TotalEnergyDeposit']
#                         n_events_recoil_not_tracked += 1
#                 else:
#                     # TODO deal with this case
#                     print('*' * 100)
#                 n_events_full_energy_deposit += 1
#             else:
#                 n_events_escape_a += 1 # (=> e.g. escape without recoil e-)
#                 # utils.print_hits_short(pandas.DataFrame([row1.values], columns=row1.index))
#             n_events_primary += 1
#         else:
#             # TODO to verify
#             if row1['TrackID'] == 1:
#                 n_events_secondary += 1
#             else:
#                 n_events_escape_b += 1
#
#         if apex:
#             cosT = 1 - (0.511 * E1) / (source_MeV * (source_MeV - E1))
#             cones.append([eventid] + apex + direction + [cosT] + [200])
#
#
#
#     print(f"{n_events_primary} events with primary particles")
#     print(f"{n_events_full_energy_deposit} events with full energy deposit")
#     print(f"{n_events_secondary} events with secondary particles")
#     print(f"{n_events_escape_a} events a with escape")
#     print(f"{n_events_escape_b} events b with escape")
#     print(f"{n_events_photoelectric} events with photoelectric absorption")
#     print(f"{n_events_recoil_tracked} events valid with recoil e- tracked")
#     print(f"{n_events_recoil_not_tracked} events valid with recoil e- not tracked")
#
#     return cp.array(cones)

def hits2cones_byEventID(file_path, source_MeV, nentries=None, store_info=False):
    if not os.path.isfile(file_path):
        sys.exit(f"File {file_path} does not exist, probably no hit produced...")
    hits = uproot.open(file_path)['Hits'].arrays(library='pd', entry_stop=nentries)  # None to read all entries
    n_events = hits['EventID'].nunique()
    print(f"{n_events} events interacted in the sensor")
    grouped = hits.groupby('EventID')
    cones = []

    # TODO: deal with doppler, fluorescence,
    n_events_primary = 0
    n_events_full_energy_deposit = 0
    for eventid, group in grouped:
        apex, direction, E1 = False, False, False
        # Sensor received primary gamma and it interacted TODO: is this correct with radioisotope source?
        if eventid != 809: continue
        if 1 in group['TrackID'].values:
            n_events_primary += 1
            # All primary energy was deposited
            if round(group['TotalEnergyDeposit'].sum(), 6) == source_MeV:  # round to avoid float precision issues
                n_events_full_energy_deposit += 1
                print_hits_inG4format(group)
                group = group.sort_values('GlobalTime') # IMPORTANT !
                print_hits_inG4format(group)
                first_hit = group.iloc[0]
                # Gamma interacts via Compton, step has dE !=0 and is stored (recoil e- not tracked)
                if first_hit['TrackID'] == 1 and group['TrackID'].value_counts()[1] > 1:
                        # if value_counts()[1] == 1, TrackID 1 stopped at 1st step via photoelec (without prior Compton)
                        # TODO: what about rayleigh scattering and pair production?
                        apex = [first_hit['PostPosition_X'], first_hit['PostPosition_Y'], first_hit['PostPosition_Z']]
                        direction = [-first_hit['PostDirection_X'], -first_hit['PostDirection_Y'], -first_hit['PostDirection_Z']]
                        E1 = first_hit['TotalEnergyDeposit']
                # Gamma interacts via Compton, step has dE = 0 and is not stored, but recoil e- tracked with TrackID=2
                # However I can't use direction of recoil e-... Need to go further
                elif first_hit['TrackID'] == 2 and first_hit['TrackCreatorProcess'] == 'compt':
                        apex = [first_hit['PrePosition_X'], first_hit['PrePosition_Y'], first_hit['PrePosition_Z']]
                        E1 = first_hit['KineticEnergy']
                        # Remove TrackID 2 and its descendants from group
                        def find_descendants(df, parent_id):
                            descendants = set()
                            children = df[df['ParentID'] == parent_id]['TrackID'].values
                            for child in children:
                                descendants.add(child)
                                descendants.update(find_descendants(df, child))
                            return descendants
                        descendants_of_2 = find_descendants(group, 2)
                        group = group[~group['TrackID'].isin(descendants_of_2.union({2}))]
                        print_hits_inG4format(group)
                        second_hit = group.iloc[0]
                        # if post-Compton step of TrackID 1 has dE != 0, it is stored and is the next one in the
                        # time-sorted group, and it gives the direction
                        if second_hit['TrackID'] == 1:
                            direction = [-second_hit[f'PreDirection_{axis}'] for axis in 'XYZ']
                        # if not, there is a new track whose origin can be used to calculate the direction
                        else:
                            prepos = cp.array([second_hit[f'PrePosition_{axis}'] for axis in 'XYZ'])
                            direction = ((cp.array(apex) - prepos) / cp.linalg.norm(cp.array(apex) - prepos)).tolist()

        if apex:
            cosT = 1 - (0.511 * E1) / (source_MeV * (source_MeV - E1))
            cones.append([eventid] + apex + direction + [cosT] + [200])

    print(f"{n_events_primary} events with primary particles")
    print(f"{n_events_full_energy_deposit} events with full energy deposit")
    return cp.array(cones)