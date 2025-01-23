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
import imaging.ComptonCamera_tests.Gate10.tools.utils as utils

pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 1000)
pandas.set_option('display.float_format', lambda x: f'{x:.3}')  # G4 steps are logged with f'{x:.3}'


# TODO: I need one version writing array for direct reco and one with extra simu info for validation?
def hits2cones_withDepth_byEventID(file_path, source_MeV, nentries=None, store_info=False):
    if not os.path.isfile(file_path):
        sys.exit(f"File {file_path} does not exist, probably no hit produced...")
    hits = uproot.open(file_path)['Hits'].arrays(library='pd', entry_stop=nentries)  # None to read all entries
    utils.print_hits_simple(hits)  # , sys.exit()
    n_events = hits['EventID'].nunique()
    print(f"{n_events} events interacted in the sensor")
    grouped = hits.groupby('EventID')
    cones = []

    # For now I only care about compton interactions from primary gamma with full energy deposited in sensor
    # TODO: deal with
    #   low cuts
    #   doppler
    #   PIXE/fluo
    #   e- was tracked
    n_events_secondary, n_events_partial_edeposit, n_events_photoelectric = 0, 0, 0
    for eventid, group in grouped:
        row1 = group.iloc[0]
        # Sensor received primary gamma
        if row1['TrackID'] == 1:
            # All primary energy was deposited
            if group['TotalEnergyDeposit'].sum() == source_MeV:
                first_process = row1['ProcessDefinedStep']
                # Compton interaction, recoil e- tracked
                if first_process == 'compt':
                    print(eventid, 'recoil e- was tracked')
                    apex = [row1['PostPosition_X'], row1['PostPosition_Y'], row1['PostPosition_Z']]
                    direction = [-row1['PostDirection_X'], -row1['PostDirection_Y'], -row1['PostDirection_Z']]
                    apex2 = [row1['PrePosition_X'], row1['PrePosition_Y'], row1['PrePosition_Z']]
                    direction2 = [-row1['PreDirection_X'], -row1['PreDirection_Y'], -row1['PreDirection_Z']]
                    # TODO which is correct? direction and direction2 seem the same
                    E1 = source_MeV - row1['TotalEnergyDeposit']
                    cosT = 1 - (0.511 * E1) / (source_MeV * (source_MeV - E1))
                    cone = apex + direction + [cosT] + [200]
                    cones.append(cone + [eventid] if store_info else cone)
                # Several possible cases
                elif first_process == 'Transportation':
                    # Photo-electric absorption
                    if group['TrackID'].value_counts()[1] == 1:
                        n_events_photoelectric += 1
                    # Compton interaction, recoil e- not tracked
                    else:
                        # TODO put this back
                        # print(eventid, 'recoil e- was not tracked')
                        # apex = [row1['PostPosition_X'], row1['PostPosition_Y'], row1['PostPosition_Z']]
                        # direction = [-row1['PostDirection_X'], -row1['PostDirection_Y'],-row1['PostDirection_Z']]
                        # E1 = row1['TotalEnergyDeposit']
                        # cosT = 1 - (0.511 * E1) / (source_MeV * (source_MeV - E1))
                        # cone = apex + direction + [cosT] + [200]
                        # cones.append(cone + [eventid] if store_info else cone)
                        continue
                else:
                    print('*' * 100)
            else:
                n_events_partial_edeposit += 1
        else:
            n_events_secondary += 1

    print(f"{round(100 * n_events_secondary / n_events)}  % events from secondary particles")
    print(f"{round(100 * n_events_partial_edeposit / n_events)}  % events with partial energy deposit")
    print(f"{round(100 * n_events_photoelectric / n_events)}  % events with photoelectric absorption")
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
