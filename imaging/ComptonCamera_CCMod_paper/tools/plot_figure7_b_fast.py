import sys
import time
import cupy as cp
import napari
import uproot
from uproot.extras import pandas
import matplotlib.pyplot as plt

path = '../output/test_data/'
energy_cut = '(energy1+energyR>0.6) & (energy1+energyR<1.275)'  # MeV (adapt to E0)
E0 = 1.275  # MeV, incident gamma energy (adapt to energy_cut)
plane_side = 100  # mm, centered at (0, 0) in world coordinates
plane_bins = 100
plane_z = range(0, 1, 1)  # mm, z-coordinates of planes perpendicular
xedges = cp.linspace(-plane_side / 2, plane_side / 2, plane_bins + 1)
yedges = cp.linspace(-plane_side / 2, plane_side / 2, plane_bins + 1)
# G4double m_E1; // energy deposition of the first interaction
# G4double m_E2; // energy deposition of the second interaction
# G4double m_ER; // Total energy deposition except E1
# G4ThreeVector m_Pos1;  //
# G4ThreeVector  m_Pos2; //  Second interaction
# G4ThreeVector  m_Pos3; //  third interaction

tree = uproot.open(path + 'CC_Cones.root:Cones')
print(tree.num_entries, 'entries in tree Cones')
df_cone = tree.arrays(cut=energy_cut, library='pd')


def stack_ellipses(df, z_plane):
    # Extract necessary parameters from DataFrame
    apex = cp.array(df[['globalPosX1', 'globalPosY1', 'globalPosZ1']].values)
    direction = apex - cp.array(df[['globalPosX2', 'globalPosY2', 'globalPosZ2']].values)
    direction = direction / cp.linalg.norm(direction, axis=1, keepdims=True)
    energy1 = cp.array(df['energy1'].values)
    cosT = 1 - (0.511 * energy1) / (E0 * (E0 - energy1))

    # Calculate ellipse parameters in plane
    dot_products = direction[:, 2]
    d = (z_plane - apex[:, 2]) / dot_products
    center = apex + d[:, None] * direction # intersection points between cone's axes and plane
    sinT = cp.sqrt(1 - cosT ** 2)
    radii = cp.abs(d * sinT / cosT)
    maj_d = cp.cross(direction, cp.array([0, 0, 1])) # major axis direction
    maj_d /= cp.linalg.norm(maj_d, axis=1, keepdims=True) # normalize major axis direction
    min_d = cp.cross(cp.array([0, 0, 1]), maj_d) # minor axis direction (normalized)
    maj_l = radii / cp.sqrt(1 - dot_products ** 2) # major axis length
    min_l = radii # minor axis length

    # Generate ellipse points
    ellipse_angle_grid = cp.linspace(0, 2 * cp.pi, 1000)
    c = cp.cos(ellipse_angle_grid)
    s = cp.sin(ellipse_angle_grid)
    x = center[:, 0][:, None] + maj_l[:, None] * c * maj_d[:, 0][:, None] + min_l[:, None] * s * min_d[:, 0][:, None]
    y = center[:, 1][:, None] + maj_l[:, None] * c * maj_d[:, 1][:, None] + min_l[:, None] * s * min_d[:, 1][:, None]

    hist, _, _ = cp.histogram2d(x.ravel(), y.ravel(), bins=[xedges, yedges], density=False)
    # hist[hist > 0] = 1 # TODO binarize individual ellipses instead of the whole stack
    return hist


# ### Multiple 2D histograms ###
for z in plane_z:
    tstart = time.time()
    hist = stack_ellipses(df_cone, z)
    print('Time taken:', time.time() - tstart)
    plt.imshow(hist.get(), origin='lower')
    plt.colorbar()
    plt.title(f'z = {z}')
    plt.show()

# ### 3D volume ####
# tstart = time.time()
# hist_stack = cp.array([stack_ellipses(df_cone[:], z) for z in plane_z])
# print('Time taken:', time.time() - tstart)
# napari.view_image(hist_stack.get(), rgb=False, colormap='viridis')
# napari.run()
