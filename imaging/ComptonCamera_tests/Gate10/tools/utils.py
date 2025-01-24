# Prints hits like G4 steps are logged via sim.g4_verbose_level_tracking
# If pandas.set_option('display.float_format'...) is used in script calling the function, remove it
# Make sure that columns were present in simulation settings
def print_hits_inG4format(hits_df):
    print(hits_df[['PostPosition_X', 'PostPosition_Y', 'PostPosition_Z', 'KineticEnergy', 'TotalEnergyDeposit',
                   'StepLength', 'TrackLength', 'HitUniqueVolumeID', 'ProcessDefinedStep', 'ParticleName', 'TrackID',
                   'ParentID', 'ParentParticleName']])


# Prints only few relevant columns from hits tree
# Make sure that columns were present in simulation settings
def print_hits_short(hits_df):
    print(hits_df[['EventID', 'TrackID', 'ParticleName', 'ParentID', 'ParentParticleName', 'KineticEnergy',
                   'TotalEnergyDeposit', 'ProcessDefinedStep', 'TrackCreatorProcess']].to_string(index=False))

def print_hits_long(hits_df):
    print(hits_df[['EventID', 'TrackID', 'ParticleName', 'ParentID', 'ParentParticleName', 'KineticEnergy',
                   'TotalEnergyDeposit', 'ProcessDefinedStep', 'TrackCreatorProcess', 'PrePosition_X', 'PrePosition_Y',
                   'PrePosition_Z', 'PostPosition_X', 'PostPosition_Y', 'PostPosition_Z']].to_string(index=False))

# Prints directional info from hits tree
# Make sure that columns were present in simulation settings
def print_hits_direction(hits_df):
    print(hits_df[['EventID', 'TrackID', 'ParticleName', 'ProcessDefinedStep',
                   'PrePosition_X', 'PrePosition_Y', 'PrePosition_Z', 'PostPosition_X', 'PostPosition_Y', 'PostPosition_Z',
                   'PreDirection_X','PreDirection_Y', 'PreDirection_Z', 'PostDirection_X', 'PostDirection_Y',
                   'PostDirection_Z']].to_string(index=False))
