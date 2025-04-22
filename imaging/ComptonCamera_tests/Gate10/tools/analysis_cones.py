# Utility functions to analyse output files
# Can be used in the main simulation script after sim.run() or offline (i.e. reading root files without simulation)
# Calling E1 the energy deposited in the Compton scattering, as in CCMod paper

import os
import sys
import time

import pandas
import uproot
from analysis_pixelClusters import X_um, Y_um, EVENTID, ENERGY_keV
from tools.utils import *
from opengate.logger import global_log

pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 1000)
pandas.set_option('display.float_format', lambda x: f'{x:.9}')  # G4 step: .3

cones_columns = ['EventID', 'Apex_X', 'Apex_Y', 'Apex_Z', 'Direction_X',
                 'Direction_Y', 'Direction_Z', 'cosT', 'error']


# TODO: can be optimized using hits.keep_zero_edep = True in simulation settings
# TODO: reformat and refactor
def gHits2cones_byEvtID(file_path, source_MeV):
    if not os.path.isfile(file_path):
        sys.exit(f"File {file_path} does not exist, probably no hit produced.")
    else:
        global_log.info(f"Offline [cones]: START")
        global_log.debug(f"Input {file_path}")

    stime = time.time()
    hits = uproot.open(file_path)['Hits'].arrays(library='pd')
    grouped = hits.groupby('EventID')
    cones = []

    n_events_primary = 0
    n_events_full_edep = 0
    for eventid, grp in grouped:
        apex, direction, E1 = False, False, False
        # Sensor received primary gamma and it interacted TODO: is this correct with radioisotope source?
        if 1 in grp['TrackID'].values:
            n_events_primary += 1
            # All primary energy was deposited
            if round(grp['TotalEnergyDeposit'].sum(), 6) == source_MeV:
                # TODO round above is to avoid float precision issues
                n_events_full_edep += 1
                grp = grp.sort_values('GlobalTime')  # IMPORTANT !
                h = grp.iloc[0]
                # Gamma interacts via Compton, step has dE !=0 and is stored (recoil e- not tracked)
                if h['TrackID'] == 1 and grp['TrackID'].value_counts()[1] > 1:
                    # if value_counts()[1] == 1, TrackID 1 stopped at 1st step via photoelec (without prior Compton)
                    # TODO: what about rayleigh scattering and pair production?
                    apex = [h[f'PostPosition_{axis}'] for axis in 'XYZ']
                    direction = [-h[f'PostDirection_{axis}'] for axis in 'XYZ']
                    E1 = h['TotalEnergyDeposit']
                # Gamma interacts via Compton, step has dE = 0 and is not stored, but recoil e- tracked with TrackID=2
                # However I can't use direction of recoil e-... Need to go further
                elif h['TrackID'] == 2 and h['TrackCreatorProcess'] == 'compt':
                    apex = [h[f'PrePosition_{axis}'] for axis in 'XYZ']
                    E1 = h['KineticEnergy']

                    # Remove TrackID 2 and its descendants from group
                    def find_descendants(df, part_id):
                        descendants = set()
                        child = df[df['ParentID'] == part_id]['TrackID'].values
                        for child in child:
                            descendants.add(child)
                            descendants.update(find_descendants(df, child))
                        return descendants

                    desc_of_2 = find_descendants(grp, 2)
                    grp = grp[~grp['TrackID'].isin(desc_of_2.union({2}))]
                    h2 = grp.iloc[0]
                    # if post-Compton step of TrackID 1 has dE != 0, it is stored and is the next one in the
                    # time-sorted group, and it gives the direction
                    if h2['TrackID'] == 1:
                        direction = [-h2[f'PreDirection_{ax}'] for ax in 'XYZ']
                    # if not, there is a new track whose origin can be used to calculate the direction
                    else:
                        prepos = [h2[f'PrePosition_{axis}'] for axis in 'XYZ']
                        diff = np.array(apex) - np.array(prepos)
                        direction = (diff / np.linalg.norm(diff)).tolist()
        if apex:
            cosT = 1 - (0.511 * E1) / (source_MeV * (source_MeV - E1))
            cones.append([eventid] + apex + direction + [cosT] + [200])

    global_log.debug(f"{n_events_primary} events with primary particles")
    global_log.debug(f"{n_events_full_edep} events with full energy deposit")
    global_log.debug(f"{len(cones) or sys.exit('No cones')} cones")
    global_log.info(f"Offline [cones]: STOP. Time: {time.time() - stime:.1f} seconds.\n" + '-' * 80)
    return pandas.DataFrame(cones, columns=cones_columns)


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
    global_log.info(f"Offline [cones]: START")
    global_log.debug(f"Input pixel clusters dataframe")
    stime = time.time()

    grouped = pixelClusters.groupby(EVENTID)
    grouped = [group for group in grouped if len(group[1]) == 2]

    cones = []

    for eventid, group in grouped:
        # TODO: 1) Distinguish compton vs photo-electric interactions
        group = group.sort_values(ENERGY_keV)
        # print(group)
        clust_photoel = group.iloc[0]
        clust_compton = group.iloc[1]

        # TODO: 2) Calculate depth difference
        # delta_z = ... charge_carrier_speed * (TOA_photoelec - TOA_compton)

        # TODO: 3) Calculate absolute depth of Compton interaction (apex)
        z_compton_um = thickness_um / 2
        # OR
        # use cluster size (and energy?)

        # TODO: 4) Complete 3D positions
        pos_compton = [clust_compton[X_um], clust_compton[Y_um], z_compton_um]
        pos_photoelec = [clust_photoel[X_um], clust_photoel[Y_um],
                         thickness_um]

        # TODO: 5) Construct cone
        apex = pos_compton
        direction = np.array(apex) - np.array(pos_photoelec)
        direction = (direction / np.linalg.norm(direction)).tolist()
        E1_MeV = clust_photoel[ENERGY_keV] / 1000
        cosT = 1 - (0.511 * E1_MeV) / (source_MeV * (source_MeV - E1_MeV))
        apex = [apex[0] / 1000, apex[1] / 1000, apex[2] / 1000]
        cones.append([eventid] + apex + direction + [cosT] + [200])

    global_log.debug(f"{len(cones)} cones")
    global_log.info(f"Offline [cones]: STOP. Time: {time.time() - stime:.1f} seconds.\n" + '-' * 80)
    return pandas.DataFrame(cones, columns=cones_columns)


def tpxCones2simuCoordinates(cones, sensor):
    cones = cones.copy()
    sensor_size = sensor.size
    sensor_position = sensor.translation
    sensor_rotation = sensor.rotation  # TODO: to include
    cones['Apex_X'] = cones['Apex_X'] + sensor_position[0] - sensor_size[0] / 2
    cones['Apex_Y'] = cones['Apex_Y'] + sensor_position[1] - sensor_size[1] / 2
    cones['Apex_Z'] = cones['Apex_Z'] + sensor_position[2] - sensor_size[2] / 2
    return cones
