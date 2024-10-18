import numpy as np
import time
import cupy as np
import uproot
from uproot.extras import pandas
import matplotlib.pyplot as plt
pandas().set_option('display.max_columns', 100), pandas().set_option('display.width', 1000)

path = '../output/test_data/'
# energy_cut = '(energy1+energyR>0.6)' # MeV
energy_cut = '(energy1+energyR>0.6) & (energy1+energyR<1.275)' # MeV
energy_tot = 1.275 # MeV
r = 50
bins = 100
xedges = np.linspace(-r, r, 101)
yedges = np.linspace(-r, r, 101)

tree = uproot.open(path + 'CC_Cones.root:Cones')
print(tree.num_entries, 'entries in tree Cones')
df = tree.arrays(cut=energy_cut,library='pd')

# TODO: another way to reconstruct the 3D image, looping over 3D volume voxels

# Define the 3D volume
volume_size = (100, 100, 100)  # Example volume size
volume = np.zeros(volume_size)

# Example data: list of events with apex, direction vector, and opening angle
events = [
    {'apex': np.array([50, 50, 0]), 'direction': np.array([0, 0, 1]), 'angle': np.pi / 6},
    # Add more events as needed
]


# Function to check if a point is inside a cone
def is_point_in_cone(point, apex, direction, angle):
    v = point - apex
    v_norm = np.linalg.norm(v)
    if v_norm == 0:
        return False
    cos_theta = np.dot(v, direction) / v_norm
    return cos_theta >= np.cos(angle)


# Back-projection
for event in events:
    apex = event['apex']
    direction = event['direction'] / np.linalg.norm(event['direction'])
    angle = event['angle']

    for x in range(volume_size[0]):
        for y in range(volume_size[1]):
            for z in range(volume_size[2]):
                point = np.array([x, y, z])
                if is_point_in_cone(point, apex, direction, angle):
                    volume[x, y, z] += 1

# Normalize the volume
volume /= len(events)

# The volume now contains the reconstructed 3D image