import sys
import subprocess
import uproot


def run_allpix(sim, output_dir='allpix/', log_level='FATAL'):
    # TODO: simulate timewalk / fToA !
    # TODO: simulate ToT (DefaultDigitizer or CSADigitizer?)
    # TODO: is DetectorHistogrammer necessary? slow?
    hits_actor = sim.actor_manager.get_actor("Hits")
    hits_file = sim.output_dir + '/' + hits_actor.output_filename
    gateHits_df = uproot.open(hits_file)['Hits'].arrays(library='pd')
    if sim.visu is True:
        sys.exit("Allpix cannot be run with Gate visualization enabled")
    else:
        print(f"Running Allpix2 with input {hits_file},{gateHits_df.size} hits")

    sensor = sim.volume_manager.get_volume("sensor")
    pixel = sim.volume_manager.get_volume("pixel_param")
    source = sim.source_manager.get_source("source")

    # TODO deal with sensor rotation/orientation
    geometry_conf_content = f"""[0_0]
type = "detector_model"
position = {sensor.translation}
orientation = 0 0 0 # sensor.rotation not working
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

    main_conf_content = f"""[Allpix]
log_level = {log_level}
log_format = "DEFAULT"
detectors_file = "geometry.conf"
number_of_events = {source.n if source.n else gateHits_df['EventID'].max() + 1}
model_paths = ["."]
output_directory = "."
random_seed = 1
[DepositionReader]
model = "root"
file_name = "../{hits_file}"
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

    with open(output_dir + 'detector_model.conf',
              'w') as detector_model_conf_file:
        detector_model_conf_file.write(detector_model_conf_content)

    with open(output_dir + 'main.conf', 'w') as main_conf_file:
        main_conf_file.write(main_conf_content)

    binary_path = '/home/billoud/workspace/allpix-squared/install-noG4/bin/allpix'

    # os.system(f'{binary_path} -c {output_dir}main.conf')

    subprocess.run([binary_path, '-c', output_dir + 'main.conf'], check=True)


# Different simulation (sub-)chains for Allpix
# https://allpix-squared.docs.cern.ch/docs/03_getting_started/06_simulation_chain/
# QDC: charge-to-digital converter
# TDC: time-to-digital converter
# https://allpix-squared.docs.cern.ch/docs/08_modules/defaultdigitizer/

# For basic tests
# => input hits do not always produce output pixel hits
# TODO pixelID does not always match the pixelID in the output...
chain_simple = """
[GenericPropagation]
[SimpleTransfer]
max_depth_distance = 1m
[DefaultDigitizer]
threshold = 0e
"""

chain_advanced = """
[ElectricFieldReader]
model = "constant"
bias_voltage = -1000V
[GenericPropagation]
mobility_model = "constant"
mobility_electron = 10000cm*cm/V/s
mobility_hole = 500cm*cm/V/s
[PulseTransfer]
[DefaultDigitizer]
threshold = 1e
threshold_smearing = 0
qdc_resolution = 8 # Resolution of the QDC in units of bits. Thus, a value of 8 would translate to a QDC range of 0 to 255. A value of 0bit switches off the QDC simulation and returns the actual charge in electrons. Defaults to 0.
qdc_smearing = 0 # Standard deviation of the Gaussian noise in the ADC conversion (after applying the threshold). Defaults to 300 electrons.
qdc_slope = 10e # Slope of the QDC calibration in electrons per ADC unit (unit: e). Defaults to 10e.
qdc_offset = -1 # Offset of the QDC calibration in electrons. In order to simulate a ToT (time-over-threshold) device, this offset should be configured to the negative value of the threshold. Defaults to 0.
tdc_resolution = 0 # Resolution of the TDC in units of bits. Thus, a value of 8 would translate to a TDC range of 0 to 255. A value of 0bit switches off the TDC simulation and returns the actual time of arrival in nanoseconds. Defaults to 0.
tdc_smearing = 0
tdc_slope = 0 # Slope of the TDC calibration in nanoseconds per TDC unit (unit: ns). Defaults to 10ns.
tdc_offset = 0 # Offset of the TDC calibration in nanoseconds. Defaults to 0.
"""

# TODO
chain_advanced_csa = """
[TransientPropagation]
[PulseTransfer]
[CSADigitizer]
"""
