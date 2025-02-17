import sys
import subprocess
import pandas as pd
import uproot

from imaging.ComptonCamera_tests.Gate10.tools.utils import compute_pixel_id


def run_allpix(sim, output_dir='allpix/'):
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
log_level = "FATAL"
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
branch_names = ["EventID", "TotalEnergyDeposit", "GlobalTime", "Position_X", "Position_Y", "Position_Z", "HitUniqueVolumeID", "PDGCode", "TrackID", "ParentID"]
output_plots = true
[GenericPropagation]
temperature = 293K
charge_per_step = 100
[SimpleTransfer]
max_depth_distance = 100mm
[DefaultDigitizer]
threshold = 1e
[DetectorHistogrammer]
name = "0_0" # !!! EDIT !!!
# [ROOTObjectWriter]
[TextWriter]
include = "PixelHit"
    """

    # Step 2: Write the content to the respective .conf files
    with open(output_dir + 'geometry.conf', 'w') as geometry_conf_file:
        geometry_conf_file.write(geometry_conf_content)

    with open(output_dir + 'detector_model.conf', 'w') as detector_model_conf_file:
        detector_model_conf_file.write(detector_model_conf_content)

    with open(output_dir + 'main.conf', 'w') as main_conf_file:
        main_conf_file.write(main_conf_content)

    binary_path = '/home/billoud/workspace/allpix-squared/install-noG4/bin/allpix'

    # os.system(f'{binary_path} -c {output_dir}main.conf')

    subprocess.run([binary_path, '-c', output_dir + 'main.conf'], check=True)


def pixelHitAllpixTxt2pixelHit(text_file):
    records = []

    # Read file and parse data
    with open(text_file, "r") as file:
        event_id = None
        for line in file:
            line = line.strip()

            # Check for event ID
            if line.startswith("==="):
                event_id = int(line.split()[1]) - 1 # allpix adds 1 to event ID
                continue

            # Skip lines starting with '---'
            if line.startswith("---"):
                continue

            # Process PixelHit lines
            if line.startswith("PixelHit"):
                parts = line.split()
                x, y = int(parts[1].strip(',')), int(parts[2].strip(','))
                pixel_id = compute_pixel_id(x, y)
                pixel_charge = float(parts[3].strip(','))
                global_time = float(parts[5].strip(','))
                position_x = float(parts[6].strip(','))
                position_y = float(parts[7].strip(','))
                position_z = float(parts[8].strip(','))

                records.append([event_id, pixel_id, int(global_time), int(pixel_charge/100),  position_x, position_y, position_z])

    df = pd.DataFrame(records, columns=["EventID", "PixelID", "GlobalTime", "PixelCharge",  "PositionX", "PositionY",
                                        "PositionZ"])

    return df


def gHits2pixelHits_allpix(sim, output_dir='allpix/', nentries=None):
    run_allpix(sim, output_dir)
    return pixelHitAllpixTxt2pixelHit(output_dir + 'data.txt')

def save_pixelHits_burdaman_format(pixelHits_df, output_path):
    # TODO set types correctly (else visu with TrackLab will not work)
    # TODO => https://software.utef.cvut.cz/tracklab/manual/a01627.html
    pixelHits_df['fTOA'] = 0
    pixelHits_df[['PixelID', 'GlobalTime', 'fTOA', 'PixelCharge']].to_csv(output_path, header=False, index=False, sep='\t')

    # Define the custom header
    custom_header = """# Start of measurement: 10/1/2017 17:34:41.8467094
# Start of measurement - unix time: 1506872081.846
# Chip ID: H3-W00036
# Readout IP address: 192.168.1.105
# Back-end location: Satigny, CH
# Detector mode: ToA & ToT
# Readout mode: Data-Driven Mode
# Bias voltage: 229.72V
# THL = 1570 (0.875V)
# Sensor temperature: 58.9°C
# Readout temperature: 42.9°C
# ------- Internal DAC values ---------------
# Ibias_Preamp_ON:\t128\t(1.208V)
# Ibias_Preamp_OFF:\t8\t(1.350V)
# VPreamp_NCAS:\t\t128\t(0.702V)
# Ikrum:\t\t15\t(1.128V)
# Vfbk:\t\t164\t(0.891V)
# Vthreshold_fine:\t505\t(0.877V)
# Vthreshold_coarse:\t7\t(0.875V)
# Ibias_DiscS1_ON:\t100\t(1.109V)
# Ibias_DiscS1_OFF:\t8\t(1.321V)
# Ibias_DiscS2_ON:\t128\t(0.396V)
# Ibias_DiscS2_OFF:\t8\t(0.256V)
# Ibias_PixelDAC:\t128\t(0.984V)
# Ibias_TPbufferIn:\t128\t(1.169V)
# Ibias_TPbufferOut:\t128\t(1.077V)
# VTP_coarse:\t\t128\t(0.693V)
# VTP_fine:\t\t256\t(0.724V)
# Ibias_CP_PLL:\t\t128\t(0.557V)
# PLL_Vcntrl:\t\t128\t(0.874V)
# BandGap output:\t--- \t(0.684V)
# BandGap_Temp:\t\t--- \t(0.733V)
# Ibias_dac:\t\t--- \t(1.241V)
# Ibias_dac_cas:\t\t--- \t(1.004V)
# DACs: \t128\t8\t128\t15\t164\t505\t7\t100\t8\t128\t8\t128\t128\t128\t128\t256\t128\t128
# DACs Scans: \t1.208V\t1.350V\t0.702V\t1.128V\t0.891V\t0.877V\t0.875V\t1.109V\t1.321V\t0.396V\t0.256V\t0.984V\t1.169V\t1.077V\t0.693V\t0.724V\t0.557V\t0.874V\t0.684V\t0.733V\t1.241V\t1.004V
# -----------------------------------------------------------------------------------------------------------------------------
"""

    # Read the CSV file and add the custom header
    with open(output_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    lines.insert(0, custom_header)

    # Write the modified content back to the file
    with open(output_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)