import sys
import uproot
#from compton import compton_forward
import os
compton_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "/home/billoud/PycharmProjects/COMPTON/mw_forward"))
sys.path.append(compton_dir)
from compton import compton_forward
import cupy as cp
import awkward as ak
import napari

##############################################################
# Settings
##############################################################
# path = '/home/billoud/PycharmProjects/GateContrib/imaging/ComptonCamera_CCMod_paper/output/seed1_time100/'
# path = '/home/billoud/PycharmProjects/GateContrib/imaging/ComptonCamera_CCMod_paper/output/test_data/'
path = '/home/billoud/PycharmProjects/GateContrib/imaging/ComptonCamera_tests/single_layer/output/'
#energy_cut = '(energy1+energyR>0.6) & (energy1+energyR<1.275)'  # MeV, see section 2.2.3 of the paper
energy_cut = 'energy1>0'
energy_cut = '(energy1>0) & (nSingles==2)'

E0 = 0.250 # MeV, incident gamma energy (adapt to energy_cut)
# E0 = 0.1405 # MeV, incident gamma energy (adapt to energy_cut)
vsize = (256, 256, 256)
vpitch = 1
inv_cos_error = 100


##############################################################
# Load Data obtained from CCMod's hidden exectuable 'GateDigit_seqCoinc2Cones'
# TODO: could load seqCoincidences tree directly (with some processing) to avoid the need for GateDigit_seqCoinc2Cones
##############################################################
tree = uproot.open(path + 'CC_Cones.root:Cones')
# tree = uproot.open(path + 'CC_Cones.root:Cones')
print(tree.num_entries, 'entries in tree Cones')
fields = ['energy1', 'globalPosX1', 'globalPosY1', 'globalPosZ1', 'globalPosX2', 'globalPosY2', 'globalPosZ2']
ak_array = tree.arrays(fields, cut=energy_cut)[:]
print(len(ak_array['energy1']), 'entries after cuts')
cp_array = cp.stack([ak.to_cupy(ak_array[field]) for field in fields], axis=-1)

##############################################################
# Convert data to standard cone parameters
##############################################################
vectorX = cp_array[:, 1] - cp_array[:, 4]
vectorY = cp_array[:, 2] - cp_array[:, 5]
vectorZ = cp_array[:, 3] - cp_array[:, 6]
magnitude = cp.sqrt(vectorX ** 2 + vectorY ** 2 + vectorZ ** 2)
nX = vectorX / magnitude
nY = vectorY / magnitude
nZ = vectorZ / magnitude
cosT = 1 - (0.511 * cp_array[:, 0]) / (E0 * (E0 - cp_array[:, 0]))
inv_cos_error = inv_cos_error * cp.ones_like(cosT)
cp_array = cp.stack([cp_array[:, 1], cp_array[:, 2], cp_array[:, 3], nX, nY, nZ, cosT, inv_cos_error], axis=-1)
# [ apex_x, y, z, normalized_direction_x, y, z, cosine_of_cone_half_angle, inverse_of_cosine_error]
# print(cp_array[:])#, sys.exit()

##############################################################
# Move origin to volume center
##############################################################
cp_array[:, 0] = cp_array[:, 0] + vpitch * vsize[0] / 2
cp_array[:, 1] = cp_array[:, 1] + vpitch * vsize[1] / 2
cp_array[:, 2] = cp_array[:, 2] + vpitch * vsize[2] / 2

##############################################################
# Do Projection
##############################################################
vol = cp.zeros(vsize, dtype=cp.float32)
vol = compton_forward(vol, cp_array, volume_pitch=vpitch)

##############################################################
# Display results
##############################################################
# vol = cp.swapaxes(vol, 0, 1)
# cp.save("vol.npy", vol)
#napari.view_image(vol.get(), colormap='gray_r')
#napari.run()
viewer = napari.Viewer()
viewer.add_image(vol.get(), colormap='gray', name='Volume')

# Add a red cube to the center of the volume
cube_size = 5
center = (vsize[0] // 2, vsize[1] // 2, vsize[2] // 2)
red_voxel = cp.zeros(vsize, dtype=cp.float32)
half_size = cube_size // 2
red_voxel[center[0] - half_size:center[0] + half_size + 1,
          center[1] - half_size:center[1] + half_size + 1,
          center[2] - half_size:center[2] + half_size + 1] = 1.0
viewer.add_image(red_voxel.get(), colormap='red', name='Red Voxel', blending='additive')

napari.run()