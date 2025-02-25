# Some utility functions

# WARNING: For print functions, make sure that dataframe columns are present in simulation settings (c.f. actor attribtues)

import numpy as np


# Prints hits like G4 steps are logged via sim.g4_verbose_level_tracking
# If pandas.set_option('display.float_format'...) is used in script calling the function, remove it
def print_hits_inG4format(hits_df):
    print(
        hits_df[['PostPosition_X', 'PostPosition_Y', 'PostPosition_Z', 'KineticEnergy', 'TotalEnergyDeposit',
                 'StepLength', 'TrackLength', 'HitUniqueVolumeID', 'ProcessDefinedStep', 'ParticleName', 'TrackID',
                 'ParentID', 'ParentParticleName',
                 'TrackCreatorProcess', 'TrackCreatorModelName'
                 ]])


# Prints only few relevant columns from hits tree
def print_hits_short(hits_df):
    print(hits_df[['EventID', 'TrackID', 'ParticleName', 'ParentID', 'ParentParticleName', 'KineticEnergy',
                   'TotalEnergyDeposit', 'ProcessDefinedStep', 'TrackCreatorProcess', 'GlobalTime',
                   'HitUniqueVolumeID']].to_string(index=False))


def print_hits_long(hits_df):
    print(hits_df[[
        'EventID', 'TrackID', 'ParticleName', 'ParentID', 'ParentParticleName', 'KineticEnergy',
        'TotalEnergyDeposit', 'ProcessDefinedStep', 'TrackCreatorProcess',
        'PrePosition_X', 'PrePosition_Y', 'PrePosition_Z', 'PostPosition_X', 'PostPosition_Y', 'PostPosition_Z',
        'PreDirection_X', 'PreDirection_Y', 'PreDirection_Z', 'PostDirection_X', 'PostDirection_Y', 'PostDirection_Z'
    ]].to_string(index=False))


# Prints directional info from hits tree
# PreDirection and PostDirection seem to be the same very frequently but not always
def print_hits_direction(hits_df):
    print(hits_df[[
        'EventID', 'TrackID', 'ParticleName', 'ProcessDefinedStep',
        'PrePosition_X', 'PrePosition_Y', 'PrePosition_Z', 'PostPosition_X', 'PostPosition_Y', 'PostPosition_Z',
        'PreDirection_X', 'PreDirection_Y', 'PreDirection_Z', 'PostDirection_X', 'PostDirection_Y', 'PostDirection_Z'
    ]].to_string(index=False))


# Prints time info
def print_hits_time(hits_df):
    print(hits_df[[
        'EventID', 'TrackID', 'ParticleName', 'GlobalTime', 'PreGlobalTime', 'LocalTime', 'TimeFromBeginOfEvent',
        'TrackProperTime',
    ]].to_string(index=False))


# Prints processes info
def print_hits_processes(hits_df):
    print(hits_df[[
        'EventID', 'TrackID', 'ParticleName', 'ProcessDefinedStep', 'TrackCreatorProcess', 'TrackCreatorModelName'
    ]].to_string(index=False))


def print_hits_inG4format_sortedByGlobalTime(hits_df):
    hits_df = hits_df.groupby('EventID').apply(lambda x: x.sort_values('GlobalTime'))
    print_hits_inG4format(hits_df)


def print_hits_long_sortedByGlobalTime(hits_df):
    hits_df = hits_df.groupby('EventID').apply(lambda x: x.sort_values('GlobalTime'))
    print_hits_long(hits_df)


def compute_pixel_id(x, y):
    return x * 256 + y  # Assuming 256x256 pixel grid (adjust if needed)


def sum_time_intervals(time_intervals):
    return sum([time_interval[1] - time_interval[0] for time_interval in time_intervals])


def get_pointSourcePhi(sensor, source):
    sensor_position = np.array(sensor.translation)
    source_position = np.array(source.position.translation)
    sensor_size = np.max(sensor.size[0:1])
    distance = np.linalg.norm(sensor_position - source_position)-sensor.size[2]/2
    phi_deg = 180 - np.degrees(np.arctan(sensor_size / (2 * distance)))
    return phi_deg
