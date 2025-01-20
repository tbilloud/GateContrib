import opengate as gate
import imaging.ComptonCamera_tests.Gate10.tools.analysis_basics as analysis_basics
import imaging.ComptonCamera_tests.Gate10.tools.analysis_cones as analysis_cones

sim = gate.Simulation()
sim.output_dir = "output"

um = gate.g4_units.um
mm = gate.g4_units.mm
keV = gate.g4_units.keV
MeV = gate.g4_units.MeV
deg = gate.g4_units.deg

## ===========================
## == LOAD DATABASE         ==
## ===========================
sim.volume_manager.add_material_database('../data/GateMaterials.db')

# ===========================
# ==   GEOMETRY            ==
# ===========================
npix = 1000
pitch, thickness = 55 * um, 1000 * mm
sim.world.material = "Vacuum"
sim.world.size = [npix * pitch, npix * pitch, thickness * 2]
sensor = sim.add_volume("Box", "sensor")
sensor.size = [npix * pitch, npix * pitch, thickness]
sensor.translation = [0 * mm, 0 * mm, thickness / 2]
sensor.material = "CdTe"
# pixel = sim.add_volume("Box", "pixel")
# pixel.mother = sensor.name
# pixel.size = [pitch, pitch, thickness]
# pixel.material = "CdTe" # Tungsten CdTe
# pixel.color = [0, 0, 0, 0]  # see trajectories better
# pixel.translation = gate.geometry.utility.get_grid_repetition([int(npix * pitch / pitch)] * 2 + [1], [pitch, pitch, 0])

## ===========================
## ==  PHYSICS              ==
## ===========================
# fluo = True
# doppler = True
# if doppler:
#     sim.physics_manager.physics_list_name = 'G4EmLivermorePhysics'  # FTFP_BERT_LIV, G4EmStandardPhysics, G4EmLivermorePhysics, G4EmStandardPhysics_option4
# if fluo:
#     sim.physics_manager.global_production_cuts.all = 0.1 * um
#     sim.physics_manager.em_parameters.update(
#         {'fluo': fluo, 'auger': fluo, 'auger_cascade': fluo, 'pixe': fluo, 'deexcitation_ignore_cut': fluo})

## =============================
## == ACTORS                  ==
## =============================
# HITS
hc = sim.add_actor('DigitizerHitsCollectionActor', 'Hits')
hc.attached_to = sensor.name
hc.authorize_repeated_volumes = True # required according to doc, but seems useless
hc.output_filename = 'CC_Hits.root'
hc.attributes = ['EventID', 'TrackID', 'ParentID', 'ParentParticleName', 'ParticleName', 'KineticEnergy',
                 'TotalEnergyDeposit', 'TrackCreatorProcess', 'ProcessDefinedStep',
                 # 'PreKineticEnergy', 'PostKineticEnergy', # KineticEnergy == PreKineticEnergy
                 'PrePosition', 'EventPosition',
                 'PreStepUniqueVolumeID', 'PostPosition', 'GlobalTime'  # for DigitizerAdderActor
                 ]
# SINGLES
sc = sim.add_actor("DigitizerAdderActor", "Singles")
sc.input_digi_collection = "Hits"
sc.policy = "EnergyWeightedCentroidPosition"
sc.output_filename = 'CC_Singles.root'  # if hc.output_filename, there will be two branches in the file
# TIMEPIX FRAME (HIT COUNT)
proj = sim.add_actor("DigitizerProjectionActor", "Projection")
proj.input_digi_collections = ["Singles"]
proj.spacing = [pitch, pitch]  # Set pixel spacing in mm
proj.size = [npix, npix]  # Image size in pixels (128x128)
proj.output_filename = 'projection.mhd'

## =============================
## == VERBOSITY               ==
## =============================
# sim.g4_verbose, sim.g4_verbose_level_tracking = True, 1

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
source.position.translation = [0 * mm, 0 * mm, -thickness / 2]

##====================================================
##  R A N D O M   E N G I N E  A N D  S E E D
##====================================================
sim.random_engine = "MersenneTwister"
sim.random_seed = 1

##=====================================================
##   M E A S U R E M E N T
##=====================================================
source.n = 30
# source.activity = 10 * gate.g4_units.Bq # for sorting coincidences with GlobalTime
sim.run()

##=====================================================
##   ANALYSIS
##=====================================================
# analysis_basics.analyse_hits(sim.output_dir + '/' + hc.output_filename)
# analysis.analyse_singles(sim.output_dir + '/' + sc.output_filename)
# plot_DigitizerProjectionActor(sim)
# TODO: running hits_visualizer.py here does not work...
# analysis_cones.extract_ideal_hits(sim.output_dir + '/' + hc.output_filename)
analysis_cones.hits2cones_withDepth_byEventID(sim.output_dir + '/' + hc.output_filename, source.energy.mono)
# analysis_cones.singles2cones_withDepth_byEventID(sim.output_dir + '/' + sc.output_filename)