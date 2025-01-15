import pandas
import uproot
import SimpleITK as sitk
import matplotlib.pyplot as plt
from pandas import Series

pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 100)
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
def analyse_hits(sim):
    hc = sim.actor_manager.get_actor("Hits")
    tree_hits = uproot.open(sim.output_dir + '/' + hc.output_filename)['Hits']
    print('\n =>', tree_hits.num_entries, 'entries in tree Hits')
    # print(tree.keys())
    hits = tree_hits.arrays(library='pd', entry_stop=None)  # None to read all entries
    hits.loc[:, hits.columns.str.contains('Energy')] *= 1000  # convert to keV
    hits.loc[:, hits.columns.str.contains('Position')] *= 1000  # convert to um
    print(hits.to_string(index=False))
    # print(hits.groupby('EventID').first().to_string(index=False))
    print(hits[hits['ParticleName'] == 'gamma'].to_string(index=False))
    # print(hits['TotalEnergyDeposit'].sum())
    # print(hits[hits['TrackID']==2]['TotalEnergyDeposit'].sum())

def analyse_singles(sim):
    sc = sim.actor_manager.get_actor("Singles")
    tree_singles = uproot.open(sim.output_dir + '/' + sc.output_filename)['Singles']
    print('\n =>', tree_singles.num_entries, 'entries in tree Singles')
    singles = tree_singles.arrays(library='pd', entry_stop=None)  # None to read all entries
    singles.loc[:, singles.columns.str.contains('Energy')] *= 1000  # convert to keV
    singles.loc[:, singles.columns.str.contains('Position')] *= 1000  # convert to um
    # print(singles.to_string(index=False))
    print(Series(singles['PreStepUniqueVolumeID'].to_numpy()).value_counts(normalize=True) * 100,'\n')  # !! entry_stop = None  !!

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
