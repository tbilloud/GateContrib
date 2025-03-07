# Basic backprojection reconstruction for Compton camera data
# Very slow, ~1 sec per cone
# Use cupy-based reconstruction if possible

from tools.display_reconstruction import *

def reco_bp(cones_df, vpitch, vsize=(256, 256, 256),
            napari=False, det=False):

    volume = np.zeros(vsize, dtype=np.float32)
    grid_x = np.linspace(-vsize[0] // 2, vsize[0] // 2, vsize[0]) * vpitch
    grid_y = np.linspace(-vsize[1] // 2, vsize[1] // 2, vsize[1]) * vpitch
    grid_z = np.linspace(-vsize[2] // 2, vsize[2] // 2, vsize[2]) * vpitch
    X, Y, Z = np.meshgrid(grid_x, grid_y, grid_z, indexing='ij')

    for _, c in cones_df.iterrows():

        apex = np.array([c['Apex_X'], c['Apex_Y'], c['Apex_Z']])
        d = np.array([c['Direction_X'], c['Direction_Y'], c['Direction_Z']])
        cosT = c['cosT']

        # Compute distance from apex to each voxel
        voxel_vec = np.stack([X - apex[0], Y - apex[1], Z - apex[2]],axis=-1)
        voxel_distances = np.linalg.norm(voxel_vec, axis=-1)

        # Compute angle with direction vector
        vox_vec_norm = voxel_vec / np.expand_dims(voxel_distances, axis=-1)
        dot_products = np.sum(vox_vec_norm * d, axis=-1)

        # Compute mask of voxels satisfying the Compton cone condition
        tolerance = 0.01  # Adjust tolerance as needed
        cone_mask = np.abs(dot_products - cosT) < tolerance

        # Accumulate contribution to the volume
        volume[cone_mask] += 1


    volume = np.swapaxes(volume, 0, 1)
    if napari:
        display_reconstruction(volume, vsize, vpitch, det)

    return volume