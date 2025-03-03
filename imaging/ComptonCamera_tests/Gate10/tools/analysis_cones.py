# Utility functions to analyse output files
# Can be used in the main simulation script after sim.run() or offline (i.e. reading root files without simulation)
# Calling E1 the energy deposited in the Compton scattering, as in CCMod paper
import os
import sys
import numpy as np
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


def gHits2cones_byEventID(file_path, source_MeV, nentries=None, to_array=False):
    if not os.path.isfile(file_path):
        sys.exit(f"File {file_path} does not exist, probably no hit produced...")
    else:
        print(f"Reading {file_path} for cone analysis")
    hits = uproot.open(file_path)['Hits'].arrays(library='pd', entry_stop=nentries)  # None to read all entries
    n_events = hits['EventID'].nunique()
    print(f"{n_events} events interacted in the sensor")
    grouped = hits.groupby('EventID')
    cones = []

    n_events_primary = 0
    n_events_full_energy_deposit = 0
    for eventid, group in grouped:
        apex, direction, E1 = False, False, False
        # Sensor received primary gamma and it interacted TODO: is this correct with radioisotope source?
        # if eventid != 809: continue
        if 1 in group['TrackID'].values:
            n_events_primary += 1
            # All primary energy was deposited
            if round(group['TotalEnergyDeposit'].sum(), 6) == source_MeV:  # round to avoid float precision issues
                n_events_full_energy_deposit += 1
                # print_hits_inG4format(group)
                group = group.sort_values('GlobalTime')  # IMPORTANT !
                # print_hits_inG4format(group)
                first_hit = group.iloc[0]
                # Gamma interacts via Compton, step has dE !=0 and is stored (recoil e- not tracked)
                if first_hit['TrackID'] == 1 and group['TrackID'].value_counts()[1] > 1:
                    # if value_counts()[1] == 1, TrackID 1 stopped at 1st step via photoelec (without prior Compton)
                    # TODO: what about rayleigh scattering and pair production?
                    apex = [first_hit['PostPosition_X'], first_hit['PostPosition_Y'], first_hit['PostPosition_Z']]
                    direction = [-first_hit['PostDirection_X'], -first_hit['PostDirection_Y'],
                                 -first_hit['PostDirection_Z']]
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
                    # print_hits_inG4format(group)
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

    if to_array:
        print('=>', cones.shape[0] if cones.shape[0] else sys.exit('No cones'),
              'cones,', cp.isnan(cones).any(axis=1).sum(),
              'with NaNs')
        return cp.array(cones)
    else:
        return pandas.DataFrame(cones, columns=['EventID', 'Apex_X', 'Apex_Y', 'Apex_Z', 'Direction_X', 'Direction_Y',
                                                'Direction_Z', 'cosT', 'error'])
