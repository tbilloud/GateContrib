import sys
import time
import cupy as cp
import napari
import uproot
from uproot.extras import pandas
import matplotlib.pyplot as plt
pandas().set_option('display.max_columns', 100), pandas().set_option('display.width', 1000)

path = '../output/test_data/'
# energy_cut = '(energy1+energyR>0.6)' # MeV
energy_cut = '(energy1+energyR>0.6) & (energy1+energyR<1.275)' # MeV (adapt to E0)
E0 = 1.275 # MeV, incident gamma energy (adapt to energy_cut)

tree = uproot.open(path + 'CC_Cones.root:Cones')
print(tree.num_entries, 'entries in tree Cones')
df = tree.arrays(cut=energy_cut, library='pd')

def stack_ellipses(df, z_plane):
    # Extract necessary columns
    g_10 = cp.array(df[['globalPosX1', 'globalPosY1', 'globalPosZ1']].values)
    g_21 = cp.array(df[['globalPosX2', 'globalPosY2', 'globalPosZ2']].values)
    energy1 = cp.array(df['energy1'].values)

    # Calculate normalized direction vectors of cones
    direction_vectors = (g_21 - g_10) / cp.linalg.norm(g_21 - g_10, axis=1, keepdims=True)

    # Calculate opening angles of cones
    cosT = 1 - (0.511 * energy1) / (E0 * (E0 - energy1))

    # Calculate intersection points between cones and plane perpendicular to z-axis
    dot_products = direction_vectors[:, 2]
    d = (z_plane - g_10[:, 2]) / dot_products
    intersect = g_10 + d[:, None] * direction_vectors

    # Calculate ellipse parameters in plane
    sinT = cp.sqrt(1 - cosT ** 2)
    radii = cp.abs(d * sinT / cosT)
    maj_d = cp.cross(direction_vectors, cp.array([0, 0, 1]))
    maj_d /= cp.linalg.norm(maj_d, axis=1, keepdims=True)
    min_d = cp.cross(cp.array([0, 0, 1]), maj_d)
    maj_l = radii / cp.sqrt(1 - dot_products ** 2)
    min_l = radii

    # Generate ellipse points
    ellipse_angle_grid = cp.linspace(0, 2 * cp.pi, 1000)
    c = cp.cos(ellipse_angle_grid)
    s = cp.sin(ellipse_angle_grid)
    x = intersect[:, 0][:, None] + maj_l[:, None] * c * maj_d[:, 0][:, None] + min_l[:, None] * s * min_d[:, 0][:, None]
    y = intersect[:, 1][:, None] + maj_l[:, None] * c * maj_d[:, 1][:, None] + min_l[:, None] * s * min_d[:, 1][:, None]

    print(x.shape, y.shape)

    hist, _, _ = cp.histogram2d(x.ravel(), y.ravel(), bins=[xedges, yedges], density=True)
    # hist[hist > 0] = 1 # TODO binarize individual ellipses instead of the whole stack
    return hist



plane_side = 100 # mm, centered at (0, 0) in world coordinates
plane_bins = 100
plane_z = range(0, 51, 50) # mm, z-coordinates of planes perpendicular
xedges = cp.linspace(-plane_side / 2, plane_side / 2, plane_bins + 1)
yedges = cp.linspace(-plane_side / 2, plane_side / 2, plane_bins + 1)

# Separate 2D histograms for each z-plane
for z in plane_z:
    tstart = time.time()
    hist = stack_ellipses(df[2:3], z)
    print('Time taken:', time.time() - tstart)
    plt.imshow(hist.get(), origin='lower')
    plt.colorbar()
    plt.title(f'z = {z}')
    plt.show()

# # # 3D histogram stack
# tstart = time.time()
# hist_stack = cp.array([stack_ellipses(df[:], z) for z in plane_z])
# print('Time taken:', time.time() - tstart)
# napari.view_image(hist_stack.get(), rgb=False, colormap='viridis')
# napari.run()
