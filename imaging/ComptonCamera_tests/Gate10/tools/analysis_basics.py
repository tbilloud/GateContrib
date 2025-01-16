# Utility functions to analyse output files
# Can be used in the main simulation script after sim.run() or offline (i.e. reading root files without simulation)

import pandas
import uproot
import SimpleITK as sitk
import matplotlib.pyplot as plt
import cupy as cp
from pandas import Series

pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 1000)
pandas.set_option('display.float_format', lambda x: f'{x:.9f}')

# List of all possible attributes for Hits:
# ['Direction', 'EventDirection', 'EventID', 'EventKineticEnergy', 'EventPosition', 'GlobalTime', 'HitUniqueVolumeID',
# 'KineticEnergy', 'LocalTime', 'PDGCode', 'ParentID', 'ParentParticleName', 'ParticleName', 'ParticleType', 'Position',
# 'PostDirection', 'PostKineticEnergy', 'PostPosition', 'PostPositionLocal', 'PostStepUniqueVolumeID', 'PostStepVolumeCopyNo',
# 'PreDirection', 'PreDirectionLocal', 'PreGlobalTime', 'PreKineticEnergy', 'PrePosition', 'PrePositionLocal', 'PreStepUniqueVolumeID',
# 'PreStepVolumeCopyNo', 'ProcessDefinedStep', 'RunID', 'StepLength', 'ThreadID', 'TimeFromBeginOfEvent', 'TotalEnergyDeposit',
# 'TrackCreatorModelIndex', 'TrackCreatorModelName', 'TrackCreatorProcess', 'TrackID', 'TrackLength', 'TrackProperTime',
# 'TrackVertexKineticEnergy', 'TrackVertexMomentumDirection', 'TrackVertexPosition', 'TrackVolumeCopyNo', 'TrackVolumeInstanceID',
# 'TrackVolumeName', 'UnscatteredPrimaryFlag', 'Weight']
# Obtained with print(opengate_core.GateDigiAttributeManager.GetInstance().GetAvailableDigiAttributeNames())
def analyse_hits(file_path):
    tree_hits = uproot.open(file_path)['Hits']
    print('\n =>', tree_hits.num_entries, 'entries in tree Hits')
    # print(tree.keys())
    hits = tree_hits.arrays(library='pd', entry_stop=None)  # None to read all entries
    hits.loc[:, hits.columns.str.contains('Energy')] *= 1000  # convert to keV
    hits.loc[:, hits.columns.str.contains('Position')] *= 1000  # convert to um
    # print(hits.to_string(index=False))
    # print(hits.groupby('EventID').first().to_string(index=False))
    # print(hits[hits['ParticleName'] == 'gamma'].to_string(index=False))
    print(hits[hits['TrackCreatorProcess'] == 'compt'].to_string(index=False))
    # print(hits['TotalEnergyDeposit'].sum())
    # print(hits[hits['TrackID']==2]['TotalEnergyDeposit'].sum())

# List of available attributes for Singles:
#  EventID  TrackID  ParentID  ParentParticleName  ParticleName  KineticEnergy  TotalEnergyDeposit  TrackCreatorProcess
#  ProcessDefinedStep     Position_X     Position_Y    Position_Z  PreStepUniqueVolumeID  PostPosition_X  PostPosition_Y
#  PostPosition_Z GlobalTime
def analyse_singles(file_path):
    tree_singles = uproot.open(file_path)['Singles']
    print('\n =>', tree_singles.num_entries, 'entries in tree Singles')
    singles = tree_singles.arrays(library='pd', entry_stop=None)  # None to read all entries
    singles.loc[:, singles.columns.str.contains('Energy')] *= 1000  # convert to keV
    singles.loc[:, singles.columns.str.contains('Position')] *= 1000  # convert to um
    # print(singles.to_string(index=False))
    print(singles[singles['TrackCreatorProcess'] == 'compt'].to_string(index=False))
    # print(Series(singles['PreStepUniqueVolumeID'].to_numpy()).value_counts(normalize=True) * 100,'\n')  # !! entry_stop = None  !!
    singles = singles.loc[:, ~singles.columns.str.contains('Position', case=False)]
    return singles

def plot_DigitizerProjectionActor(sim):

    proj = sim.actor_manager.get_actor("Projection")

    # Load the .mhd file
    file_path = sim.output_dir + '/' + proj.output_filename  # Replace with the actual path to your .mhd file
    image = sitk.ReadImage(file_path)

    # Convert to a NumPy array for plotting
    image_array = sitk.GetArrayFromImage(image)
    plt.imshow(image_array[0, :, :], cmap='gray', vmax=2)
    plt.colorbar()
    plt.show()
