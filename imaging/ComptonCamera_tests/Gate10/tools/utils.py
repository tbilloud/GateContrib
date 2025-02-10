# WARNING: Make sure that columns were present in simulation settings


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
                   'TotalEnergyDeposit', 'ProcessDefinedStep', 'TrackCreatorProcess']].to_string(index=False))


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
