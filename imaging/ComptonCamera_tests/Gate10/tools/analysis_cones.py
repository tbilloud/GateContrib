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
import pandas as pd
from pandas import Series
from analysis_pixelClusters import X_um, Y_um, EVENTID, ENERGY_keV
import tools.analysis_basics as analysis_basics
from tools.utils import *
from tools.utils import print_hits_inG4format
from opengate.logger import global_log

pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 1000)
pandas.set_option('display.float_format', lambda x: f'{x:.9}')  # G4 steps are logged with f'{x:.3}'

# TODO: can be optimized using hits.keep_zero_edep = True in simulation settings
# TODO: reformat and refactor
def gHits2cones_byEvtID(file_path, source_MeV):
    if not os.path.isfile(file_path):
        sys.exit(f"File {file_path} does not exist, probably no hit produced...")
    else:
        global_log.info(f"Offline: cone analysis with input {file_path}")

    hits = uproot.open(file_path)['Hits'].arrays(library='pd')  # None to read all entries
    grouped = hits.groupby('EventID')
    cones = []

    n_events_primary = 0
    n_events_full_energy_deposit = 0
    for eventid, group in grouped:
        apex, direction, E1 = False, False, False
        # Sensor received primary gamma and it interacted TODO: is this correct with radioisotope source?
        if 1 in group['TrackID'].values:
            n_events_primary += 1
            # All primary energy was deposited
            if round(group['TotalEnergyDeposit'].sum(), 6) == source_MeV:  # round to avoid float precision issues
                n_events_full_energy_deposit += 1
                group = group.sort_values('GlobalTime')  # IMPORTANT !
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
                    second_hit = group.iloc[0]
                    # if post-Compton step of TrackID 1 has dE != 0, it is stored and is the next one in the
                    # time-sorted group, and it gives the direction
                    if second_hit['TrackID'] == 1:
                        direction = [-second_hit[f'PreDirection_{axis}'] for axis in 'XYZ']
                    # if not, there is a new track whose origin can be used to calculate the direction
                    else:
                        prepos = np.array([second_hit[f'PrePosition_{axis}'] for axis in 'XYZ'])
                        direction = ((np.array(apex) - prepos) / np.linalg.norm(np.array(apex) - prepos)).tolist()

        if apex:
            cosT = 1 - (0.511 * E1) / (source_MeV * (source_MeV - E1))
            cones.append([eventid] + apex + direction + [cosT] + [200])

    global_log.debug(f"{n_events_primary} events with primary particles")
    global_log.debug(f"{n_events_full_energy_deposit} events with full energy deposit")
    global_log.debug(f"{len(cones) if len(cones) else sys.exit('No cones')} cones")

    return pandas.DataFrame(cones, columns=['EventID', 'Apex_X', 'Apex_Y', 'Apex_Z', 'Direction_X', 'Direction_Y',
                                            'Direction_Z', 'cosT', 'error'])

# Clusters have:
# - X/Y coordinates
# - ToA
# - ToT
# Cones need:
# - Apex (X,Y,Z)
# - Direction (X,Y,Z)
# - cosT
# - error
def pixelClusters2cones_byEvtID(pixelClusters, source_MeV, thickness_um):
    global_log.info(f"Offline: cones analysis with pixel cluster input")

    grouped = pixelClusters.groupby(EVENTID)
    grouped = [group for group in grouped if len(group[1]) == 2]

    cones = []

    for eventid, group in grouped:

        # TODO: 1) Distinguish compton vs photo-electric interactions
        group = group.sort_values(ENERGY_keV)
        # print(group)
        photoelec_interaction = group.iloc[0]
        compton_interaction = group.iloc[1]

        # TODO: 2) Calculate depth difference
        # delta_z = ... charge_carrier_speed * (TOA_photoelec - TOA_compton)

        # TODO: 3) Calculate absolute depth of Compton interaction (apex)
        apex_z = thickness_um / 2
        # OR
        # use cluster size (and energy?)

        # TODO: 4) Complete 3D positions
        pos_compton = [compton_interaction[X_um], compton_interaction[Y_um], 0]
        pos_photoelec = [photoelec_interaction[X_um], photoelec_interaction[Y_um], thickness_um]

        # TODO: 5) Construct cone
        apex = pos_compton
        direction = np.array(apex) - np.array(pos_photoelec)
        direction = (direction / np.linalg.norm(direction)).tolist()
        E1_MeV = photoelec_interaction[ENERGY_keV] / 1000
        cosT = 1 - (0.511 * E1_MeV) / (source_MeV * (source_MeV - E1_MeV))
        apex_mm = [apex[0] / 1000, apex[1] / 1000, apex[2] / 1000]
        cones.append([eventid] + apex_mm + direction + [cosT] + [200])

    global_log.debug(f"{len(cones)} cones")

    return pandas.DataFrame(cones, columns=['EventID', 'Apex_X', 'Apex_Y', 'Apex_Z', 'Direction_X', 'Direction_Y',
                                            'Direction_Z', 'cosT', 'error'])


def tpxCones2simuCoordinates(cones, sensor):
    cones = cones.copy()
    sensor_size = sensor.size
    sensor_position = sensor.translation
    sensor_rotation = sensor.rotation # TODO: to include
    cones['Apex_X'] = cones['Apex_X'] + sensor_position[0] - sensor_size[0] / 2
    cones['Apex_Y'] = cones['Apex_Y'] + sensor_position[1] - sensor_size[1] / 2
    cones['Apex_Z'] = cones['Apex_Z'] + sensor_position[2] - sensor_size[2] / 2
    return cones