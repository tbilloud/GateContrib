import numpy as np
import uproot
from uproot.extras import pandas
import matplotlib.pyplot as plt
import pandas as pd

pandas().set_option('display.max_columns', 100), pandas().set_option('display.width', 1000)

# Define the path to the ROOT file and energy cut
path = '../output/seed1_time100/'
energy_cut = '(energy1+energyR>0.6)' # MeV
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
print(df_cone[:])

# Define the z-coordinate of the plane
z_plane = 0
r = 50
hist, xedges, yedges = np.histogram2d([], [], bins=100, range=[[-r, r], [-r, r]])


# Function to calculate all intersection points with the plane at z = z_plane and update the histogram
def calculate_intersections_with_z_plane(row, hist):
    apex = np.array([row['apex_x'], row['apex_y'], row['apex_z']])
    direction_vector = row['direction_vector']
    opening_angle = row['opening_angle']

    # Calculate the intersection points of the cone with the plane
    # TODO: the following block is wrong
    # Calculate the parameter t for the intersection
    t = (z_plane - apex[2]) / direction_vector[2]
    # Calculate the intersection point on the cone's axis
    x_intersection = apex[0] + t * direction_vector[0]
    y_intersection = apex[1] + t * direction_vector[1]
    # Calculate the radius of the intersection circle
    r = (z_plane - apex[2]) * np.tan(opening_angle)
    # Generate points on the intersection circle
    theta = np.linspace(0, 2 * np.pi, 100)
    x_circle = x_intersection + r * np.cos(theta)
    y_circle = y_intersection + r * np.sin(theta)

    # Update the histogram
    hist_update, _, _ = np.histogram2d(x_circle, y_circle, bins=[xedges, yedges])
    hist += hist_update


# Apply the function to each row in the dataframe
df_cone[:5].apply(lambda row: calculate_intersections_with_z_plane(row, hist), axis=1)

# Plot the 2D histogram
plt.figure(figsize=(8, 6))
plt.imshow(hist, origin='lower', cmap='viridis', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
plt.xlabel('x (mm)')
plt.ylabel('y (mm)')
plt.show()
