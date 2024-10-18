import time
import numpy as np
import uproot
from uproot.extras import pandas
import matplotlib.pyplot as plt
import pandas as pd
import napari

path = '../output/test_data/'
energy_cut = '(energy1+energyR>0.6) & (energy1+energyR<1.275)'  # MeV
E0 = 1.275  # MeV
plane_side = 100  # mm, centered at (0, 0) in world coordinates
plane_bins = 100
plane_z = range(0, 51, 10)  # mm, z-coordinates of planes perpendicular
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
df_cone = tree.arrays(cut=energy_cut, library='pd')[2:4]
tstart = time.time()


def stack_ellipses(row, histo, z_plane):
    # Extract necessary parameters from DataFrame
    apex = np.array([row['globalPosX1'], row['globalPosY1'], row['globalPosZ1']])
    direction = apex - [row['globalPosX2'], row['globalPosY2'], row['globalPosZ2']]
    direction = direction / np.linalg.norm(direction)
    energy1 = row['energy1']
    opening_angle = np.arccos(1 - (0.511 * energy1) / (E0 * (E0 - energy1)))
    # check if opening angle is nan
    if np.isnan(opening_angle):
        return
    else:
        # Normalize the axis
        plane_normal = np.array([0, 0, 1])
        # Calculate the cosine and sine of the cone angle
        cos_angle = np.cos(opening_angle)
        sin_angle = np.sin(opening_angle)
        # Calculate the dot product of the axis and the plane normal
        dot_product = np.dot(direction, plane_normal)
        # Check if the cone and plane are parallel
        if np.abs(dot_product) < 1e-6:
            print("The cone and plane are parallel and do not intersect.")
            return
        # Calculate the intersection point
        d = (z_plane - apex[2]) / dot_product
        intersect_p = apex + d * direction
        # Calculate the radius of the intersection ellipse
        radius = np.abs(d * sin_angle / cos_angle)  # Ensure radius is positive
        # Calculate the direction of the major and minor axes of the ellipse
        major_ax_d = np.cross(direction, plane_normal)
        major_ax_d = major_ax_d / np.linalg.norm(major_ax_d)
        minor_ax_d = np.cross(plane_normal, major_ax_d)
        # Calculate the lengths of the major and minor axes
        major_ax_l = radius / np.sqrt(1 - dot_product ** 2)
        minor_ax_l = radius
        theta = np.linspace(0, 2 * np.pi, 1000)
        # Parametric equations for the ellipse
        x_circle = intersect_p[0] + major_ax_l * np.cos(theta) * major_ax_d[0] + minor_ax_l * np.sin(theta) * minor_ax_d[0]
        y_circle = intersect_p[1] + major_ax_l * np.cos(theta) * major_ax_d[1] + minor_ax_l * np.sin(theta) * minor_ax_d[1]

        # Update the histogram
        hist_update, _, _ = np.histogram2d(x_circle, y_circle, bins=[xedges, yedges])
        ##############################################
        # TODO: for 3D reconstruction, ellipse histograms should be weighted according to distance to apex
        hist_update[hist_update > 0] = 1
        hist_update *= radius**2
        ##############################################
        histo += hist_update

hist_stack = np.zeros((len(plane_z), plane_bins, plane_bins))
for i, z in enumerate(plane_z):
    tstart = time.time()
    hist, _, _ = np.histogram2d([], [], bins=[xedges, yedges])
    df_cone.apply(lambda row: stack_ellipses(row, hist, z), axis=1)
    print('Time taken:', time.time() - tstart)

    # ### Multiple 2D histograms ###
    plt.imshow(hist, origin='lower')
    plt.colorbar()
    plt.title(f'z = {z}')
    plt.show()

    ### 3D volume ###
    hist_stack[i] = hist
napari.view_image(hist_stack, rgb=False, colormap='viridis')
napari.run()
