import sys
import opengate as gate, opengate_core
import os

sim, sim.output_dir = gate.Simulation(), "output"
um, mm, keV, MeV, deg = gate.g4_units.um, gate.g4_units.mm, gate.g4_units.keV, gate.g4_units.MeV, gate.g4_units.deg

## ===========================
## == LOAD DATABASE         ==
## ===========================
sim.volume_manager.add_material_database('data/GateMaterials.db')

# ===========================
# ==   GEOMETRY            ==
# ===========================
npix, pitch, thickness = 10, 55 * um, 100 * mm
sim.world.material = "Vacuum"
sim.world.size = [npix * pitch + 1, npix * pitch + 1, thickness * 2 + 1]  # + 1 avoids segmentation fault
sensor = sim.add_volume("Box", "sensor")
sensor.material = "CdTe"
sensor.size = [npix * pitch, npix * pitch, thickness]
sensor.translation = [0 * mm, 0 * mm, thickness / 2]
# sensor.rotation = R.from_euler('z', 45, degrees=True).as_matrix()
pixel = sim.add_volume("Box", "pixel")
pixel.mother, pixel.material, pixel.size = sensor.name, 'Tungsten', [pitch, pitch, thickness]
pixel.translation = gate.geometry.utility.get_grid_repetition([int(npix * pitch / pitch)] * 2 + [1], [pitch, pitch, 0])
# pixel.color = [0, 0, 0, 0]  # see trajectories better

## ===========================
## ==  PHYSICS              ==
## ===========================
sim.physics_manager.physics_list_name = 'G4EmLivermorePhysics'
sim.physics_manager.global_production_cuts.all = 100 * um
sim.physics_manager.em_parameters.update(
    {'fluo': True, 'pixe': True, 'deexcitation_ignore_cut': True, 'auger': True, 'auger_cascade': True})

## =============================
## == ACTORS                  ==
## =============================
hits = sim.add_actor('DigitizerHitsCollectionActor', 'Hits')
hits.attached_to = sensor.name
# hc.authorize_repeated_volumes = True  # required according to doc, but seems useless
hits.output_filename = 'CC_Hits.root'
# hits.attributes = opengate_core.GateDigiAttributeManager.GetInstance().GetAvailableDigiAttributeNames()
hits.attributes = ["EventID", "TotalEnergyDeposit", "GlobalTime", "Position", "HitUniqueVolumeID", "PDGCode", "TrackID",
                   "ParentID"]

## ============================
## ==  VISUALIZATION         ==
## ============================
# sim.visu = True  # defaults to vrml, qt seems to not work on ubuntu yet

## ============================
## == SOURCE                 ==
## ============================
source = sim.add_source("GenericSource", "source_point")
source.particle = "gamma"
source.energy.mono = 1000 * keV
# source.direction.type, source.direction.theta, source.direction.phi = "iso", [160 * deg, 180 * deg], [0, 360 * deg]
source.direction.type, source.direction.momentum = "momentum", [0, 0, 1]
source.position.translation = [0.1 * mm, 0 * mm, -thickness / 2]

##====================================================
##  R A N D O M   E N G I N E  A N D  S E E D
##====================================================
sim.random_engine, sim.random_seed = "MersenneTwister", 2

##=====================================================
##   M E A S U R E M E N T
##=====================================================
source.n = 4
sim.run()

##=====================================================
##   ANALYSIS
##=====================================================
hits_path = sim.output_dir + '/' + hits.output_filename
# analysis_basics.analyse_hits(hits_path)

##=====================================================
##   ALLPIX2 INTERFACE
##=====================================================
geometry_conf_content = """
[0_0]
type = "detector_model"
position = 0 0 50mm # !!! EDIT !!!
orientation = 0 0 0
"""
detector_model_conf_content = """
type = "hybrid"
geometry = "pixel"
number_of_pixels = 10 10
pixel_size = 55um 55um # !!! EDIT !!!
sensor_thickness = 100mm # !!! EDIT !!!
sensor_material = "cadmium_telluride" # !!! EDIT !!!
bump_sphere_radius = 9.0um
bump_cylinder_radius = 7.0um
bump_height = 20.0um
"""
main_conf_content = """
[Allpix]
log_level = "INFO"
log_format = "DEFAULT"
detectors_file = "geometry.conf"
number_of_events = 10
model_paths = ["."]
output_directory = "output"
random_seed = 1
[DepositionReader]
model = "root"
file_name = "/home/billoud/PycharmProjects/GateContrib/imaging/ComptonCamera_tests/Gate10/output/CC_Hits.root"
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
[ROOTObjectWriter]
"""

# Step 2: Write the content to the respective .conf files
with open('geometry.conf', 'w') as geometry_conf_file:
    geometry_conf_file.write(geometry_conf_content)

with open('detector_model.conf', 'w') as detector_model_conf_file:
    detector_model_conf_file.write(detector_model_conf_content)

with open('main.conf', 'w') as main_conf_file:
    main_conf_file.write(main_conf_content)

binary_path = '/home/billoud/workspace/allpix-squared/install-noG4/bin/allpix'
print('running allpix')
os.system(f'{binary_path} -c main.conf')
