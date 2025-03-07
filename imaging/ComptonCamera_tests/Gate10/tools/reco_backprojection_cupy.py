# Basic backprojection reconstruction for Compton camera data
# Cupy-based script, GPU needed, x100 faster than numpy-based version

from imaging.ComptonCamera_tests.tools.display_reconstruction import *
import cupy as cp

def reco_bp_cupy(cones_df, vpitch, vsize=(256, 256, 256),
                 napari=False, det=False):
    # Define the reconstruction volume
    volume = cp.zeros(vsize, dtype=cp.float32)
    grid_x = cp.linspace(-vsize[0] // 2, vsize[0] // 2, vsize[0]) * vpitch
    grid_y = cp.linspace(-vsize[1] // 2, vsize[1] // 2, vsize[1]) * vpitch
    grid_z = cp.linspace(-vsize[2] // 2, vsize[2] // 2, vsize[2]) * vpitch
    X, Y, Z = cp.meshgrid(grid_x, grid_y, grid_z, indexing='ij')

    for _, c in cones_df.iterrows():

        apex = cp.array([c['Apex_X'], c['Apex_Y'], c['Apex_Z']])
        d = cp.array([c['Direction_X'], c['Direction_Y'], c['Direction_Z']])
        cosT = c['cosT']

        # Compute distance from apex to each voxel
        voxel_vec = cp.stack([X - apex[0], Y - apex[1], Z - apex[2]],axis=-1)
        voxel_distances = cp.linalg.norm(voxel_vec, axis=-1)

        # Compute angle with direction vector
        vox_vec_norm = voxel_vec / cp.expand_dims(voxel_distances, axis=-1)
        dot_products = cp.sum(vox_vec_norm * d, axis=-1)

        # Compute mask of voxels satisfying the Compton cone condition
        tolerance = 0.01  # Adjust tolerance as needed
        cone_mask = cp.abs(dot_products - cosT) < tolerance

        # Accumulate contribution to the volume
        volume[cone_mask] += 1


    volume = cp.swapaxes(volume, 0, 1)
    if napari:
        display_reconstruction(volume.get(), vsize, vpitch, det)

    return volume