import sys
import time
import numpy as np
import uproot
from uproot.extras import pandas
import matplotlib.pyplot as plt
import pandas as pd
import napari
pd.set_option('display.width', 1000), pd.set_option('display.max_columns', None)

path = '../output/test_data/'
energy_cut = '(energy1+energyR>0.6) & (energy1+energyR<1.275)'  # MeV, see section 2.2.3
E0 = 1.275  # MeV, incident gamma energy (adapt to energy_cut)
plane_side = 100  # mm, plane being centered at (0, 0) in world coordinates
plane_bins = 100
plane_z = range(-50, 50, 1)  # mm, z-coordinates of planes perpendicular
n_ellipse_points = 1000
plane_cone_dirs = 1e-6

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
df_cone = tree.arrays(cut=energy_cut, library='pd')[:]
print(len(df_cone), 'entries in tree Cones after energy cuts')
print('Number of cones with at least one NaN parameter:', df_cone.isnull().any(axis=1).sum())
print(df_cone['IsTrueCoind'].value_counts())
plane_normal = np.array([0, 0, 1])
# TODO: filter bad events:
#  - false coincidences (IsTrueCoind == False)
#  - NaN values
#  - cosT out of bounds (i.e. wrong energy values)


def stack_ellipses(row, hist_stack, z_plane):

    # Extract necessary parameters from DataFrame
    apex = np.array([row['globalPosX1'], row['globalPosY1'], row['globalPosZ1']])
    direction = apex - [row['globalPosX2'], row['globalPosY2'], row['globalPosZ2']]
    direction = direction / np.linalg.norm(direction)
    E1 = row['energy1']
    cosT = 1 - (0.511 * E1) / (E0 * (E0 - E1)) # equation 1a in paper
    if cosT < -1 or cosT > 1:
        print('for z =',z_plane,'and cone number',row.name,'cosT out of bounds')

    # Calculate ellipse parameters in plane
    dot_product = np.dot(direction, plane_normal)
    d = (z_plane - apex[2]) / dot_product
    center = apex + d * direction # intersection point
    sinT = np.sqrt(1 - cosT ** 2)
    radius = np.abs(d * sinT / cosT)
    maj_d = np.cross(direction, plane_normal) # direction of the major axis
    maj_d = maj_d / np.linalg.norm(maj_d)
    min_d = np.cross(plane_normal, maj_d) # direction of the minor axis
    maj_l = radius / np.sqrt(1 - dot_product ** 2) # length of the major axis
    min_l = radius # length of the minor axis

    # Generate ellipse points
    ellipse_points = np.linspace(0, 2 * np.pi,n_ellipse_points)
    c = np.cos(ellipse_points)
    s = np.sin(ellipse_points)
    x = center[0] + maj_l * c * maj_d[0] + min_l * s * min_d[0]
    y = center[1] + maj_l * c * maj_d[1] + min_l * s * min_d[1]

    # Update the histogram
    hist_update, _, _ = np.histogram2d(x, y, bins=[xedges, yedges])
    ##############################################
    # TODO: for 3D reconstruction, ellipse histograms should be weighted according to distance to apex
    hist_update[hist_update > 0] = 1
    hist_update *= abs(apex[2]-z_plane) # radius**2
    ##############################################
    hist_stack += hist_update

vol = np.zeros((len(plane_z), plane_bins, plane_bins))
for i, z in enumerate(plane_z):
    tstart = time.time()
    hist_stack, _, _ = np.histogram2d([], [], bins=[xedges, yedges])
    df_cone.apply(lambda row: stack_ellipses(row, hist_stack, z), axis=1)
    print(i,'/',len(plane_z), 'time', round(time.time() - tstart,2),'s')

    # ### Multiple 2D histograms ###
    # if i % 10 == 0:
    #     plt.imshow(hist, origin='lower', vmax=(len(df_cone) * max(plane_z)/10))
    #     plt.colorbar()
    #     plt.title(f'z = {z}')
    #     plt.show()

    ### 3D volume ###
    vol[i] = hist_stack

napari.view_image(vol, rgb=False, colormap='viridis')
napari.run()
