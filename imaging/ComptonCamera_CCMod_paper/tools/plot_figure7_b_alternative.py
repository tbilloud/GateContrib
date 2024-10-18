import sys
import numpy as np
import time
import uproot
from uproot.extras import pandas
import matplotlib.pyplot as plt
import napari

# TODO: another way to reconstruct the 3D image, looping over 3D volume voxels
path = '../output/test_data/'
energy_cut = '(energy1+energyR>0.6) & (energy1+energyR<1.275)'  # MeV (adapt to E0)
E0 = 1.275  # MeV, incident gamma energy (adapt to energy_cut)
plane_side = 100  # mm, centered at (0, 0) in world coordinates
plane_bins = 100
plane_z = range(0, 1, 1)  # mm, z-coordinates of planes perpendicular
xedges = np.linspace(-plane_side / 2, plane_side / 2, plane_bins + 1)
yedges = np.linspace(-plane_side / 2, plane_side / 2, plane_bins + 1)
# G4double m_E1; // energy deposition of the first interaction
# G4double m_E2; // energy deposition of the second interaction
# G4double m_ER; // Total energy deposition except E1
# G4ThreeVector m_Pos1;  //
# G4ThreeVector  m_Pos2; //  Second interaction
# G4ThreeVector  m_Pos3; //  third interaction

tree = uproot.open(path + 'CC_Cones.root:Cones')
print(tree.num_entries, 'entries in tree Cones')
df_cone = tree.arrays(cut=energy_cut, library='pd')[2:3]

# Define the 3D volume
volume_size = (plane_bins, plane_bins, len(plane_z))
volume = np.zeros(volume_size)

# Function to check if a point is inside a cone
# TODO: that's for a filled cone, do it for surface
# TODO: convert world coordinates to bins
def is_point_in_cone(point, apex, direction, angle):
    v = point - apex
    cos_theta = np.dot(v, direction) / np.linalg.norm(v)
    return cos_theta >= np.cos(angle)


# Back-projection
for index, row in df_cone.iterrows():
    print(index)
    apex = np.array([row['globalPosX1'], row['globalPosY1'], row['globalPosZ1']])
    direction = apex - [row['globalPosX2'], row['globalPosY2'], row['globalPosZ2']]
    direction = direction / np.linalg.norm(direction)
    energy1 = row['energy1']
    opening_angle = np.arccos(1 - (0.511 * energy1) / (E0 * (E0 - energy1)))

    # TODO: optimize this
    for x in range(volume_size[0]):
        for y in range(volume_size[1]):
            for z in range(volume_size[2]):
                point = np.array([x, y, z])
                if is_point_in_cone(point, apex, direction, opening_angle):
                    volume[x, y, z] += 1

# Normalize the volume
volume /= len(df_cone)

# ### Multiple 2D histograms ###
for i in range(volume_size[2]):
    plt.imshow(volume[:,:,i], origin='lower')
    plt.colorbar()
    plt.title(f'z = {z}')
    plt.show()

# # ### 3D volume ###
# napari.view_image(volume, rgb=False, colormap='viridis')
# napari.run()
