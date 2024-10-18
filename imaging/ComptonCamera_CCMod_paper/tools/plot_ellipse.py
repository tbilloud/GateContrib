import sys

import numpy as np
import cupy as cp
from matplotlib import pyplot as plt
from math import pi
from matplotlib.patches import Ellipse
import time

u = 0.  # x-position of the center
v = 0.  # y-position of the center
w1, h1 = 1, 1 # half width and height of 1st ellipse
w2, h2 = 0.2, 0.8 # half width and height of 2nd ellipse
r = 1 # axes range for figure
resolution = 10000

######################################################
############# METHOD 1 ###############################
######################################################
t = np.linspace(0, 2*pi, 100)
plt.plot( u+w1*np.cos(t) , v+h1*np.sin(t) )
plt.plot( u+w2*np.cos(t) , v+h2*np.sin(t) )
plt.xlim(-r, r)
plt.ylim(-r, r)
plt.show()

######################################################
############# METHOD 2 ###############################
######################################################
# plt.figure()
# ax = plt.gca()
# ellipse1 = Ellipse(xy=(u,v), width=w1*2, height=h1*2, edgecolor='r', fc='None')
# ellipse2 = Ellipse(xy=(u,v), width=w2*2, height=h2*2, edgecolor='b', fc='None')
# ax.add_patch(ellipse1)
# ax.add_patch(ellipse2)
# ax.set_xlim(-r, r)
# ax.set_ylim(-r, r)
# plt.show()

######################################################
############# METHOD 3 ###############################
######################################################
# # TODO: simplify meshgrid/linspace with range() if integers are OK
# tstart = time.time()
# # x, y = np.meshgrid(np.linspace(-r, r, resolution), np.linspace(-r, r, resolution))
# # x, y = cp.meshgrid(cp.linspace(-r, r, resolution), cp.linspace(-r, r, resolution)) # 5x than np.meshgrid
# # x, y = np.linspace(-r, r, resolution), np.linspace(-r, r, resolution)[:, None] # 4x faster than np.meshgrid
# x, y = cp.linspace(-r, r, resolution), cp.linspace(-r, r, resolution)[:, None] # 6x faster than np.meshgrid
# ellipse1 = ((x - u) / w1) ** 2 + ((y - v) / h1) ** 2
# ellipse_surface1 = (ellipse1 > 0.9) & (ellipse1 < 1.1)
# ellipse2 = ((x - u) / w2) ** 2 + ((y - v) / h2) ** 2
# ellipse_surface2 = (ellipse2 > 0.9) & (ellipse2 < 1.1)
# print('Elapsed time: %.2f seconds' % (time.time() - tstart))
# print(ellipse_surface2.shape)
# plt.imshow(ellipse_surface1.get() + ellipse_surface2.get())
# plt.show()

######################################################
############# METHOD 4 ###############################
######################################################
#y, x = np.ogrid[:diameter, :diameter] # TODO try that option
x, y = np.linspace(-r, r, resolution), np.linspace(-r, r, resolution)[:, None] # 4x faster than np.meshgrid
ellipse_equation = ((x - u) / h1) ** 2 + ((y - v) / w1) ** 2
ellipse_array = np.isclose(ellipse_equation, 1, atol=0.05)
plt.imshow(ellipse_array, cmap='gray', origin='lower')
plt.show()
# sys.exit()

######################################################
############# METHOD 5 ###############################
######################################################
def cone_plane_intersection(apex, axis, angle, z_plane):
    # Normalize the axis
    axis = axis / np.linalg.norm(axis)

    # Plane normal is along the z-axis
    plane_normal = np.array([0, 0, 1])

    # Calculate the cosine and sine of the cone angle
    cos_angle = np.cos(angle)
    sin_angle = np.sin(angle)

    # Calculate the dot product of the axis and the plane normal
    dot_product = np.dot(axis, plane_normal)

    # Check if the cone and plane are parallel
    if np.abs(dot_product) < 1e-6:
        raise ValueError("The cone and plane are parallel and do not intersect.")

    # Calculate the intersection point
    d = (z_plane - apex[2]) / dot_product
    intersection_point = apex + d * axis

    # Calculate the radius of the intersection ellipse
    radius = np.abs(d * sin_angle / cos_angle)  # Ensure radius is positive
    print(radius)

    # Calculate the direction of the major and minor axes of the ellipse
    major_axis_direction = np.cross(axis, plane_normal)
    major_axis_direction = major_axis_direction / np.linalg.norm(major_axis_direction)
    minor_axis_direction = np.cross(plane_normal, major_axis_direction)

    # Calculate the lengths of the major and minor axes
    major_axis_length = radius / np.sqrt(1 - dot_product**2)
    minor_axis_length = radius

    return intersection_point, major_axis_length, minor_axis_length, major_axis_direction, minor_axis_direction

# Function to plot the ellipse
def plot_ellipse(intersection_point, major_axis_length, minor_axis_length, major_axis_direction, minor_axis_direction):
    # Create a grid of points
    resolution = 1000
    r = max(major_axis_length, minor_axis_length)
    # x = np.linspace(-r, r, resolution)
    # y = np.linspace(-r, r, resolution)
    # X, Y = np.meshgrid(x, y)
    #
    # # Calculate the ellipse values
    # ellipse = ((X * major_axis_direction[0] + Y * major_axis_direction[1]) / major_axis_length) ** 2 + \
    #           ((X * minor_axis_direction[0] + Y * minor_axis_direction[1]) / minor_axis_length) ** 2
    # ellipse_surface = (ellipse <= 1.1) & (ellipse >= 0.9)
    #
    # # Plot the ellipse using imshow
    # plt.imshow(ellipse_surface, extent=[-r, r, -r, r], origin='lower')
    # plt.colorbar()
    # plt.title('Ellipse in the Plane')
    # plt.xlabel('X')
    # plt.ylabel('Y')
    # plt.show()

    # Generate angle values
    theta = np.linspace(0, 2 * np.pi, 1000)

    # Parametric equations for the ellipse
    x_ellipse = intersection_point[0] + major_axis_length * np.cos(theta) * major_axis_direction[
        0] + minor_axis_length * np.sin(theta) * minor_axis_direction[0]
    y_ellipse = intersection_point[1] + major_axis_length * np.cos(theta) * major_axis_direction[
        1] + minor_axis_length * np.sin(theta) * minor_axis_direction[1]

    # Update the histogram
    hist, _, _ = np.histogram2d(x_ellipse, y_ellipse, bins=100)
    print(hist.shape)
    plt.imshow(hist, origin='lower')
    plt.colorbar()
    #plt.plot(x_ellipse, y_ellipse)
    plt.show()

# Example usage
apex = np.array([6.638571, -2.113306, 53.0])
axis = np.array([0.14528401380530584, 0.28792745924354296, 0.9])
angle = 0.35
z_plane = 0
i, major_axis_length, minor_axis_length, major_axis_direction, minor_axis_direction = cone_plane_intersection(apex, axis, angle, z_plane)
plot_ellipse(i, major_axis_length, minor_axis_length, major_axis_direction, minor_axis_direction)