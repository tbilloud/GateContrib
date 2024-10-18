import time
import numpy as np
import uproot
from uproot.extras import pandas
import matplotlib.pyplot as plt
import pandas as pd
import napari
pandas().set_option('display.max_columns', 100), pandas().set_option('display.width', 1000)

# Define the path to the ROOT file and energy cut
path = '../output/test_data/'
# energy_cut = '(energy1+energyR>0.6)' # MeV
energy_cut = '(energy1+energyR>0.6) & (energy1+energyR<1.275)' # MeV
energy_tot = 1.275 # MeV

tree = uproot.open(path + 'CC_Cones.root:Cones')
print(tree.num_entries, 'entries in tree Cones')
#print(tree.keys())
df = tree.arrays(
    ['energy1', 'energyR', 'globalPosX1', 'globalPosY1', 'globalPosZ1', 'globalPosX2', 'globalPosY2', 'globalPosZ2',
     'nSingles', 'IsTrueCoind'],
    energy_cut,
    library='pd')
# print(df[:])

# From Gate source code:
#   G4double m_E1;            // energy deposition of the first interaction
#   G4double m_E2;            // energy deposition of the second interaction
#   G4double m_ER;            // Total energy deposition except E1

tstart = time.time()

# Function to calculate the direction vector
def calculate_direction_vector(row):
    g_10 = np.array([row['globalPosX1'], row['globalPosY1'], row['globalPosZ1']])
    g_21 = np.array([row['globalPosX2'], row['globalPosY2'], row['globalPosZ2']])
    direction_vector = g_21 - g_10
    return direction_vector / np.linalg.norm(direction_vector)


# Function to calculate the opening angle
def calculate_opening_angle(row):
    E0 = row['energyR'] + row['energy1']
    E0 = 0.511 if E0 < 0.6 else 1.275
    E1 = row['energy1']
    mc2 = 0.511
    cos_theta_C = 1 - (mc2 * E1) / (E0 * (E0 - E1))
    return np.arccos(cos_theta_C)


# Add the direction vector and opening angle to the dataframe
df_cone = pd.DataFrame()
df_cone['direction_vector'] = df.apply(calculate_direction_vector, axis=1)
df_cone['opening_angle'] = df.apply(calculate_opening_angle, axis=1)
df_cone['apex_x'] = df['globalPosX1']
df_cone['apex_y'] = df['globalPosY1']
df_cone['apex_z'] = df['globalPosZ1']


# Function to calculate all intersection points with the plane at z = z_plane and update the histogram
def stack_ellipses(row, hist, z_plane):

    apex = np.array([row['apex_x'], row['apex_y'], row['apex_z']])
    direction_vector = row['direction_vector']
    opening_angle = row['opening_angle']

    # Normalize the axis
    axis = direction_vector / np.linalg.norm(direction_vector)
    # Plane normal is along the z-axis
    plane_normal = np.array([0, 0, 1])
    # Calculate the cosine and sine of the cone angle
    cos_angle = np.cos(opening_angle)
    sin_angle = np.sin(opening_angle)
    # Calculate the dot product of the axis and the plane normal
    dot_product = np.dot(axis, plane_normal)
    # Check if the cone and plane are parallel
    if np.abs(dot_product) < 1e-6:
        print("The cone and plane are parallel and do not intersect.")
        return
    # Calculate the intersection point
    d = (z_plane - apex[2]) / dot_product
    intersect_p = apex + d * axis
    # Calculate the radius of the intersection ellipse
    radius = np.abs(d * sin_angle / cos_angle)  # Ensure radius is positive
    # Calculate the direction of the major and minor axes of the ellipse
    major_ax_d = np.cross(axis, plane_normal)
    major_ax_d = major_ax_d / np.linalg.norm(major_ax_d)
    minor_ax_d = np.cross(plane_normal, major_ax_d)
    # Calculate the lengths of the major and minor axes
    major_ax_l = radius / np.sqrt(1 - dot_product**2)
    minor_ax_l = radius
    theta = np.linspace(0, 2 * np.pi, 1000)
    # Parametric equations for the ellipse
    x_circle = intersect_p[0] + major_ax_l * np.cos(theta) * major_ax_d[0] + minor_ax_l * np.sin(theta) * minor_ax_d[0]
    y_circle = intersect_p[1] + major_ax_l * np.cos(theta) * major_ax_d[1] + minor_ax_l * np.sin(theta) * minor_ax_d[1]

    # Update the histogram
    hist_update, _, _ = np.histogram2d(x_circle, y_circle, bins=[xedges, yedges])
    hist_update[hist_update > 0] = 1  # TODO
    hist += hist_update



# Define the z-coordinate of the plane
plane_side = 100 # mm, centered at (0, 0) in world coordinates
plane_bins = 100
plane_z = range(0, 51, 1) # mm, z-coordinates of planes perpendicular
xedges = np.linspace(-plane_side / 2, plane_side / 2, plane_bins + 1)
yedges = np.linspace(-plane_side / 2, plane_side / 2, plane_bins + 1)

hist_stack = np.zeros((len(plane_z), plane_bins, plane_bins))
print(len(plane_z))
for i,z in enumerate(plane_z):
    print(i, '/', len(plane_z))
    hist, _, _ = np.histogram2d([], [], bins=[xedges, yedges])
    df_cone[:].apply(lambda row: stack_ellipses(row, hist, z), axis=1)

    # # Separate 2D histograms for each z-plane
    # plt.imshow(hist, origin='lower')
    # plt.colorbar()
    # plt.title(f'z = {z_plane}')
    # plt.show()

    # 3D histogram stack
    # TODO:
    hist_stack[i] = hist

napari.view_image(hist_stack, rgb=False, colormap='viridis')
napari.run()
