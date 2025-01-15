# TODO:
#  - find out if it is possible to have hits labeled with fluorescence in output files
#  - have qt visualisation work (developer guide -> Currently, QT visualisation is not working on all architectures.)
#  - write/use an actor that works as ComptonCameraActor in Gate 9.2 with the adderComptPhotIdeal digitizer
#  - simulate Timepix3 with pixel matrix as gridDiscretization digitizer in Gate 9.2
import opengate as gate

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
sim.world.material = "Vacuum"
sim.world.size = [0.2 * mm, 0.2 * mm, 2 * mm]
sensor = sim.add_volume("Box", "sensor")
sensor_side = 110 * um
pixel_pitch = 55 * um
sensor.size = [sensor_side, sensor_side, 1 * mm]
sensor.translation = [0 * mm, 0 * mm, 0.5 * mm]
sensor.material = "Vacuum"
pixel = sim.add_volume("Box", "pixel")
pixel.mother = sensor.name
pixel.size = [pixel_pitch, pixel_pitch, 1 * mm]
pixel.material = "Tungsten"
pixel.color = [1, 1, 0, 1]
size = [int(sensor_side/pixel_pitch), int(sensor_side/pixel_pitch), 1]
tr = [pixel_pitch, pixel_pitch, 0]
pixel.translation = gate.geometry.utility.get_grid_repetition(size, tr)

## ===========================
## ==  PHYSICS              ==
## ===========================
sim.physics_manager.physics_list_name = 'G4EmLivermorePhysics'  # FTFP_BERT_LIV, G4EmStandardPhysics, G4EmLivermorePhysics, G4EmStandardPhysics_option4
sim.physics_manager.global_production_cuts.all = 10 * um
sim.physics_manager.em_parameters.fluo = True
sim.physics_manager.em_parameters.auger = True
sim.physics_manager.em_parameters.pixe = True
sim.physics_manager.em_parameters.deexcitation_ignore_cut = True

## =============================
## == ACTORS                  ==
## =============================
# HITS
hc = sim.add_actor('DigitizerHitsCollectionActor', 'Hits')
hc.attached_to = sensor.name
hc.authorize_repeated_volumes = True
hc.output_filename = 'CC_Hits.root'
hc.attributes = ['EventID', 'TrackID', 'ParentID', 'ParentParticleName', 'ParticleName', 'KineticEnergy',
                 'TotalEnergyDeposit', 'TrackCreatorProcess', 'ProcessDefinedStep', 'Position',
                  'PreStepUniqueVolumeID', 'PostPosition', 'GlobalTime' # for DigitizerAdderActor
                 ]
# SINGLES
sc = sim.add_actor("DigitizerAdderActor", "Singles")
sc.input_digi_collection = "Hits"
sc.authorize_repeated_volumes = True
sc.policy = "EnergyWeightedCentroidPosition"
sc.output_filename = 'CC_Singles.root' # if hc.output_filename, there will be two branches in the file

## =============================
## == VERBOSITY               ==
## =============================
sim.g4_verbose = False

## ============================
## ==  VISUALIZATION         ==
## ============================
# sim.visu = True # defaults to vrml, qt seems to not work on ubuntu yet

## ============================
## == SOURCE                 ==
## ============================
source = sim.add_source("GenericSource", "source_point")
source.particle = "gamma"
source.energy.mono = 200 * keV
source.direction.type = "iso"
source.direction.theta = [160 * deg, 180 * deg]
source.direction.phi = [0, 360 * deg]

##====================================================
##  R A N D O M   E N G I N E  A N D  S E E D
##====================================================
sim.random_engine = "MersenneTwister"
sim.random_seed = 1

##=====================================================
##   M E A S U R E M E N T
##=====================================================
source.n = 1
sim.run()

##=====================================================
##   ANALYSIS
##=====================================================
from imaging.ComptonCamera_tests.Gate10.tools import analysis

analysis.analyse_hits(sim)
analysis.analyse_singles(sim)
# TODO: running hits_visualizer.py here does not work...
