# TODO:
#  - find out if it is possible to have hits labeled with fluorescence in output files
#  - have qt visualisation work (developer guide -> Currently, QT visualisation is not working on all architectures.)
#  - write/use an actor that works as ComptonCameraActor in Gate 9.2 with the adderComptPhotIdeal digitizer
#  - simulate Timepix3 with pixel matrix as gridDiscretization digitizer in Gate 9.2

import opengate as gate
from imaging.ComptonCamera_tests.Gate10.tools.analysis import plot_DigitizerProjectionActor

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
npix = 3
pitch, thickness = 55 * um, 1 * mm
sim.world.material = "Vacuum"
sim.world.size = [npix * pitch, npix * pitch, thickness * 2]
sensor = sim.add_volume("Box", "sensor")
sensor.size = [npix * pitch, npix * pitch, thickness]
sensor.translation = [0 * mm, 0 * mm, thickness / 2]
sensor.material = "Vacuum"
pixel = sim.add_volume("Box", "pixel")
pixel.mother = sensor.name
pixel.size = [pitch, pitch, thickness]
pixel.material = "CdTe"
pixel.color = [0, 0, 0, 0]  # see trajectories better
pixel.translation = gate.geometry.utility.get_grid_repetition([int(npix * pitch / pitch)] * 2 + [1], [pitch, pitch, 0])

## ===========================
## ==  PHYSICS              ==
## ===========================
fluo = True
doppler = True
if doppler:
    sim.physics_manager.physics_list_name = 'G4EmLivermorePhysics'  # FTFP_BERT_LIV, G4EmStandardPhysics, G4EmLivermorePhysics, G4EmStandardPhysics_option4
if fluo:
    sim.physics_manager.global_production_cuts.all = 0.1 * um
    sim.physics_manager.em_parameters.update(
        {'fluo': fluo, 'auger': fluo, 'auger_cascade': fluo, 'pixe': fluo, 'deexcitation_ignore_cut': fluo})

## =============================
## == ACTORS                  ==
## =============================
# HITS
hc = sim.add_actor('DigitizerHitsCollectionActor', 'Hits')
hc.attached_to = sensor.name
hc.output_filename = 'CC_Hits.root'
hc.attributes = ['EventID', 'TrackID', 'ParentID', 'ParentParticleName', 'ParticleName', 'KineticEnergy',
                 'TotalEnergyDeposit', 'TrackCreatorProcess', 'ProcessDefinedStep', 'Position',
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
sim.g4_verbose = False

## ============================
## ==  VISUALIZATION         ==
## ============================
# sim.visu = True  # defaults to vrml, qt seems to not work on ubuntu yet

## ============================
## == SOURCE                 ==
## ============================
source = sim.add_source("GenericSource", "source_point")
source.particle = "gamma"
source.energy.mono = 50 * keV
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
source.n = 1000
sim.run()

##=====================================================
##   ANALYSIS
##=====================================================
from imaging.ComptonCamera_tests.Gate10.tools import analysis

# analysis.analyse_hits(sim)
analysis.analyse_singles(sim)
plot_DigitizerProjectionActor(sim)
# TODO: running hits_visualizer.py here does not work...
