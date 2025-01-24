from napari import view_image, run
from pathlib import Path
import numpy as np

def display_reconstruction(vol, vsize):

    # TODO: add cuboid representing th detector (see napari's bounding box / annotation plugin?)
    viewer = view_image(vol, translate=tuple(-v // 2 for v in vsize), axis_labels=['y', 'x', 'z'], colormap='gray_r')
    viewer.axes.visible = True
    run()


if __name__ == "__main__":
    vol = np.load(Path('../Gate10/output') / "reconstruction.npy")
    display_reconstruction(vol, (256, 256, 256))