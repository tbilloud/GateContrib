import uproot
import subprocess
import os

# This script create a ROOT tree with cone information, using a (non-documented) executable of Gate 9.2.
# The executable (GateDigit_seqCoinc2Cones) is created when compiling offline tools. See section 'Offline processing' in
# https://opengate.readthedocs.io/en/v9.2/compton_camera_imaging_simulations.html#offline-processing
#
# After running this script, you should have 2 new files, one sequenceCoincidence_new.root and one CC_Cones.root.
# The first is needed due to a bug in GateDigit_seqCoinc2Cones: it requires a sublayerID branche in the input tree which
# is not present in the sequenceCoincidence tree. Thus the script adds this branch to the tree, saves the file, and then
# runs the executable. The second file is the output of the executable. Its tree includes the following branches:
#   - energy1: energy deposited at the first interaction
#   - energyR: total deposited energy except energy1
#   - globalPosX1 , globalPosY1,  globalPosZ1: coordinates of the interaction in the first layer (scatterer)
#   - globalPosX2,  globalPosY2,  globalPosZ2: coordinates of the interaction in the second layer (absorber)
#   - nSingles, IsTrueCoind: ???
# => see GateComptonCameraCones.hh in Gate source code for more information
#
# The half angle can be computed using the formula in the CCMod paper:
# cosT = 1 - (0.511 * energy1) / (E0 * (E0 - energy1))
# where E0 is the incident gamma energy (can be set to theorical value or as the sum energy1 + energyR)

# The GateDigit_seqCoinc2Cones gives the following errors, but they can be ignored if the sublayerID is not needed:
# Error in <TTree::SetBranchAddress>: The pointer type given "Int_t" (3) does not correspond to the type needed "Long64_t" (16) by the branch: sublayerID
# Error in <TTree::SetBranchAddress>: The pointer type given "Int_t" (3) does not correspond to the type needed "Long64_t" (16) by the branch: volumeID

# ################## TO EDIT ###################
path_data = '../output/'
file_name = 'CC_sequenceCoincidence.root'
new_file_name = 'CC_sequenceCoincidence_new.root'
path_executable = '/home/billoud/workspace/gate/Gate-9.2-QT-DIGIT-install/bin/GateDigit_seqCoinc2Cones'
path_gate = '/home/billoud/workspace/gate/Gate-9.2-QT-DIGIT-install/bin'
path_geant4 = '/home/billoud/workspace/geant4/geant4-v11.0.0-DATA-OPENGL-QT-MULTITHREADOFF-install/lib'
path_root = '/home/billoud/workspace/root/root_v6.30.08.Linux-ubuntu22.04-x86_64-gcc11.4/lib'
# ##############################################

tree = uproot.open(path_data + file_name + ':sequenceCoincidence')
with uproot.recreate(path_data + new_file_name) as file:
    df = tree.arrays(library='pd')
    df['sublayerID'] = -1
    file["sequenceCoincidence"] = df
tree_new = uproot.open(path_data + 'CC_sequenceCoincidence_new.root:sequenceCoincidence')

# Set environment variables
os.environ['LD_LIBRARY_PATH'] = f"{path_gate}:{path_geant4}:{path_root}"

# Run the GateDigit_seqCoinc2Cones executable
input_file = path_data + new_file_name
output_file = path_data + 'CC_Cones.root'
subprocess.run([path_executable, input_file, output_file])
