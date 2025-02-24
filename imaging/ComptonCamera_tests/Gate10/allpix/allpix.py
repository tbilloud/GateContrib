import sys
import subprocess
import pandas as pd
import uproot

from imaging.ComptonCamera_tests.Gate10.tools.utils import compute_pixel_id
from imaging.ComptonCamera_tests.Gate10.allpix.conf_chains import *

def run_allpix(sim, output_dir='allpix/', log_level='FATAL'):
    # TODO: simulate timewalk / fToA !
    # TODO: simulate ToT (DefaultDigitizer or CSADigitizer?)
    hits_actor = sim.actor_manager.get_actor("Hits")
    hits_root_file = sim.output_dir + '/' + hits_actor.output_filename

    if sim.visu is True:
        sys.exit("Allpix cannot be run with visualization enabled")
    else:
        print(f"Converting gate hits {hits_root_file} to pixel hits using Allpix")

    sensor = sim.volume_manager.get_volume("sensor")
    pixel = sim.volume_manager.get_volume("pixel_param")
    source = sim.source_manager.get_source("source")

    # TODO deal with sensor rotation/orientation
    geometry_conf_content = f"""[0_0]
type = "detector_model"
position = {sensor.translation} # {sensor.translation[0]} {sensor.translation[1]} {sensor.translation[2]}
orientation = 0 0 0 
    """

    detector_model_conf_content = f"""type = "hybrid"
geometry = "pixel"
number_of_pixels = {pixel.linear_repeat[0]} {pixel.linear_repeat[1]}
pixel_size = {pixel.translation[0]}mm {pixel.translation[1]}mm
sensor_thickness = {sensor.size[2]}mm
sensor_material = "{sensor.material}"
bump_sphere_radius = 9.0um
bump_cylinder_radius = 7.0um
bump_height = 20.0um
    """

    nevents = source.n if source.n else uproot.open(hits_root_file)['Hits'].arrays(library='pd')['EventID'].max()
    main_conf_content = f"""[Allpix]
log_level = {log_level}
log_format = "DEFAULT"
detectors_file = "geometry.conf"
number_of_events = {nevents+1}
model_paths = ["."]
output_directory = "."
random_seed = 1
[DepositionReader]
model = "root"
file_name = "../{hits_root_file}"
tree_name = "Hits"
detector_name_chars = 3
unit_length = "mm"
unit_time = {"s" if source.n else "ns"} # if source.n is used in Gate instead of source.activity, time is not simulated, but this allows for dummy non-zero values
branch_names = ["EventID", "TotalEnergyDeposit", "GlobalTime", "Position_X", "Position_Y", "Position_Z", "HitUniqueVolumeID", "PDGCode", "TrackID", "ParentID"]
output_plots = true
{chain_simple}
[DetectorHistogrammer]
name = "0_0"
[TextWriter]
include = "PixelHit"
    """

    with open(output_dir + 'geometry.conf', 'w') as geometry_conf_file:
        geometry_conf_file.write(geometry_conf_content)

    with open(output_dir + 'detector_model.conf', 'w') as detector_model_conf_file:
        detector_model_conf_file.write(detector_model_conf_content)

    with open(output_dir + 'main.conf', 'w') as main_conf_file:
        main_conf_file.write(main_conf_content)

    binary_path = '/home/billoud/workspace/allpix-squared/install-noG4/bin/allpix'

    # os.system(f'{binary_path} -c {output_dir}main.conf')

    subprocess.run([binary_path, '-c', output_dir + 'main.conf'], check=True)

def allpixTxt2pixelHit(text_file):
    df = pd.DataFrame(columns=["EventID", "PixelID", "ToT", "ToA", "PositionX", "PositionY", "PositionZ"])
    rows = []

    with open(text_file, "r") as file:
        event_id = None
        for line in file:
            line = line.strip()

            if line.startswith("==="):
                event_id = int(line.split()[1]) - 1  # allpix adds 1 to event ID
                continue

            if line.startswith("---"):
                continue

            if line.startswith("PixelHit"):
                parts = line.split()
                x, y = int(parts[1].strip(',')), int(parts[2].strip(','))
                pixel_id = compute_pixel_id(x, y)
                tot = float(parts[3].strip(',')) # TODO: deal with different types according to simulation chain!
                toa = float(parts[4].strip(',')) # TODO: deal with different types according to simulation chain!
                global_time = float(parts[5].strip(','))
                position_x = float(parts[6].strip(','))
                position_y = float(parts[7].strip(','))
                position_z = float(parts[8].strip(','))

                rows.append({
                    "EventID": event_id,
                    "PixelID": pixel_id,
                    "ToT": tot,
                    "ToA": global_time + toa, # because ToA is measured from the beginning of the event
                    "PositionX": position_x,
                    "PositionY": position_y,
                    "PositionZ": position_z
                })

    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
    return df