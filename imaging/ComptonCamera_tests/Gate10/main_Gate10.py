# TODO:
#  - find out if it is possible to have hits labeled with fluorescence in output files
#  - have qt visualisation work (developer guide -> Currently, QT visualisation is not working on all architectures.)
#  - write/use an actor that works as ComptonCameraActor in Gate 9.2 with the adderComptPhotIdeal digitizer
#  - simulate Timepix3 with pixel matrix as gridDiscretization digitizer in Gate 9.2

# Before running script, write in terminal:
# export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=2000000

import sys
import time

import opengate as gate
import uproot
import opengate_core as gate_core
import pandas


sim = gate.Simulation()
sim.output_dir = "output"
sim.random_seed = 1

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
# ======== World=================
sim.world.material = "Vacuum"
sim.world.size = [1 * mm, 1 * mm, 2 * mm]
sensor = sim.add_volume("Box", "sensor")
sensor.size = [1 * mm, 1 * mm, 1 * mm]
sensor.translation = [0 * mm, 0 * mm, 0.5 * mm]
sensor.material = "Tungsten"

## ===========================
## ==  PHYSICS              ==
## ===========================
sim.physics_manager.physics_list_name = 'G4EmLivermorePhysics'  # FTFP_BERT_LIV, G4EmStandardPhysics, G4EmLivermorePhysics, G4EmStandardPhysics_option4
sim.physics_manager.set_production_cut("sensor", "electron", 0.1 * um)
sim.physics_manager.set_production_cut("sensor", "positron", 0.1 * um)
# sim.physics_manager.energy_range_min = 10 * eV
# sim.physics_manager.energy_range_max = 1 * MeV
sim.physics_manager.em_parameters.fluo = True
# sim.physics_manager.em_parameters.auger = True
# sim.physics_manager.em_parameters.auger_cascade = True
sim.physics_manager.em_parameters.pixe = True
sim.physics_manager.em_parameters.deexcitation_ignore_cut = True

## =============================
## == ACTORS                  ==
## =============================
stat = sim.add_actor("SimulationStatisticsActor", "Stats")
stat.output_filename = "stats_Gate10.txt"
hc = sim.add_actor('DigitizerHitsCollectionActor', 'Hits')
hc.attached_to = ['sensor']
hc.output_filename = 'CC_Gate10_Hits.root'
# hc.attributes = gate_core.GateDigiAttributeManager.GetInstance().GetAvailableDigiAttributeNames()  # all available
hc.attributes = ['EventID', 'TrackID', 'ParentID', 'ParentParticleName', 'ParticleName', 'KineticEnergy',
                 'TotalEnergyDeposit', 'TrackCreatorProcess', 'ProcessDefinedStep',
                 'Position',
                 ]
print(hc.attributes)

## =============================
## == VERBOSITY               ==
## =============================
sim.g4_verbose = False

## ============================
## ==  VISUALIZATION         ==
## ============================
# sim.visu = True
# sim.visu_type = "qt" # default vrml
# sim.visu_commands = ['# default visualization', '#/vis/open OGLS', '/vis/open OGL', '/vis/scene/create', '/vis/drawVolume worlds', '/vis/viewer/flush', '# no verbose', '/control/verbose 0', '# Work but generate txt on terminal', '/vis/scene/add/axes 0 0 0 50 cm', '/vis/scene/add/text 10 0 0 cm 20 0 0 X', '/vis/scene/add/text 0 10 0 cm 20 0 0 Y', '/vis/scene/add/text 0 0 10 cm 20 0 0 Z', '# change orientation (for debug)', '#/vis/viewer/set/upVector 0 0 1', '#/vis/viewer/set/viewpointVector 0 1 0', '#/vis/viewer/set/upVector 1 0 0', '#/vis/viewer/set/viewpointVector 0 0 1', '#/vis/viewer/set/upVector 0 1 0', '#/vis/viewer/set/viewpointVector 1 0 0', '/vis/sceneHandler/attach', '/vis/modeling/trajectories/create/drawByParticleID', '/tracking/storeTrajectory 1', '/vis/scene/endOfEventAction accumulate', '/vis/scene/add/trajectories', '/vis/viewer/set/auxiliaryEdge true']
# sim.visu_verbose = True
# sim.visu_filename = 'testimage'

## ============================
## == SOURCE                 ==
## ============================
source = sim.add_source("GenericSource", "source_point")
source.particle = "gamma"
source.energy.mono = 140 * keV
# source.direction.type = 'momentum'
# source.direction.momentum = [0, 0, 1]
source.direction.type = "iso"
source.direction.theta = [160 * deg, 180 * deg]
source.direction.phi = [0, 360 * deg]

##====================================================
##  R A N D O M   E N G I N E  A N D  S E E D
##====================================================
sim.random_engine = "MersenneTwister"

##=====================================================
##   M E A S U R E M E N T   S E T T I N G S
##=====================================================
source.n = 1
sim.run()

##=====================================================
##   ANALYSIS
##=====================================================
pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 100)
pandas.set_option('display.float_format', lambda x: f'{x:.3f}')
tree = uproot.open(sim.output_dir + '/' + hc.output_filename)['Hits']
print('\n =>', tree.num_entries, 'entries in tree Hits')
# print(tree.keys())
hits = tree.arrays(library='pd', entry_stop=None)  # None to read all entries
hits['TotalEnergyDeposit'] = hits['TotalEnergyDeposit'] * 1000  # keV
hits['KineticEnergy'] = hits['KineticEnergy'] * 1000  # keV
hits['Position_X'] = hits['Position_X'] * 1000  # um
hits['Position_Y'] = hits['Position_Y'] * 1000  # um
hits['Position_Z'] = hits['Position_Z'] * 1000  # um
print(hits.to_string(index=False))
# print(hits)
hits.to_csv('hits_output.csv', index=False)
# print(hits.groupby('EventID').first().to_string(index=False))
#print(hits[hits['ParticleName'] == 'gamma'].to_string(index=False))



