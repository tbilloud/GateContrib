import sys
import time
import cupy as cp
import napari
import uproot
from uproot.extras import pandas
import matplotlib.pyplot as plt

path = '../output/test_data/'
energy_cut = '(energy1+energyR>0.6) & (energy1+energyR<1.275)'  # MeV, see section 2.2.3 of the paper
E0 = 1.275  # MeV, incident gamma energy (adapt to energy_cut)
plane_side = 100  # mm, plane being centered at (0, 0) in world coordinates
plane_bins = 100
plane_z = range(-50, 50, 1)  # mm, z-coordinates of planes perpendicular
n_ellipse_points = 1000
plane_cone_dirs = 1e-6

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
df_cone = tree.arrays(cut=energy_cut, library='pd')[2:8]
print('Number of cones with at least one NaN parameter:', df_cone.isnull().any(axis=1).sum())
plane_normal = cp.array([0, 0, 1])


def stack_ellipses(df, z_plane):

    # Extract necessary parameters from DataFrame
    apex = cp.array(df[['globalPosX1', 'globalPosY1', 'globalPosZ1']].values)
    direction = apex - cp.array(df[['globalPosX2', 'globalPosY2', 'globalPosZ2']].values)
    direction = direction / cp.linalg.norm(direction, axis=1, keepdims=True)
    E1 = cp.array(df['energy1'].values)
    cosT = 1 - (0.511 * E1) / (E0 * (E0 - E1)) # equation 1a in paper

    # Calculate ellipse parameters in plane
    dot_products = direction[:, 2]
    # if np.abs(dot_product) < plane_cone_dirs:
    #     print("The cone and plane are parallel and do not intersect.")
    #     return
    d = (z_plane - apex[:, 2]) / dot_products
    center = apex + d[:, None] * direction # intersection points between cone's axes and plane
    sinT = cp.sqrt(1 - cosT ** 2)
    radii = cp.abs(d * sinT / cosT)
    maj_d = cp.cross(direction, cp.array(plane_normal)) # major axis direction
    maj_d /= cp.linalg.norm(maj_d, axis=1, keepdims=True) # normalize major axis direction
    min_d = cp.cross(cp.array(plane_normal), maj_d) # minor axis direction (normalized)
    maj_l = radii / cp.sqrt(1 - dot_products ** 2) # major axis length
    min_l = radii # minor axis length

    # Generate ellipse points
    ellipse_points = cp.linspace(0, 2 * cp.pi, n_ellipse_points)
    c = cp.cos(ellipse_points)
    s = cp.sin(ellipse_points)
    x = center[:, 0][:, None] + maj_l[:, None] * c * maj_d[:, 0][:, None] + min_l[:, None] * s * min_d[:, 0][:, None]
    y = center[:, 1][:, None] + maj_l[:, None] * c * maj_d[:, 1][:, None] + min_l[:, None] * s * min_d[:, 1][:, None]

    # Fill the histogram
    hist_stack, _, _ = cp.histogram2d(x.ravel(), y.ravel(), bins=[xedges, yedges], density=True)
    ##############################################
    # TODO: for 3D reconstruction, ellipse histograms should be weighted according to distance to apex
    # hist_stack[hist_stack > 0] = 1 # TODO binarize individual ellipses instead of the whole stack
    ##############################################
    return hist_stack


# ### Multiple 2D histograms ###
# for z in plane_z:
#     tstart = time.time()
#     hist = stack_ellipses(df_cone, z)
#     print('Time taken:', time.time() - tstart)
#     plt.imshow(hist.get(), origin='lower')
#     plt.colorbar()
#     plt.title(f'z = {z}')
#     plt.show()

# ### 3D volume ####
tstart = time.time()
vol = cp.array([stack_ellipses(df_cone[:], z) for z in plane_z])
print('Time taken:', time.time() - tstart)
napari.view_image(vol.get(), rgb=False, colormap='viridis')
napari.run()
