# Before running script, write in terminal:
# export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=2000000

import sys
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
absorber = sim.add_volume("Box", "absorber")
absorber.size = [1 * mm, 1 * mm, 1 * mm]
absorber.translation = [0 * mm, 0 * mm, 0.5 * mm]
absorber.material = "CdTe"

## ===========================
## ==  PHYSICS              ==
## ===========================
sim.physics_manager.physics_list_name = 'G4EmLivermorePhysics'  # FTFP_BERT_LIV, G4EmStandardPhysics, G4EmLivermorePhysics, G4EmStandardPhysics_option4
sim.physics_manager.set_production_cut("absorber", "electron", 0.1 * um)
sim.physics_manager.set_production_cut("absorber", "positron", 0.1 * um)
# sim.physics_manager.energy_range_min = 10 * eV
# sim.physics_manager.energy_range_max = 1 * MeV
sim.physics_manager.em_parameters.fluo = True
sim.physics_manager.em_parameters.auger = True
sim.physics_manager.em_parameters.auger_cascade = True
sim.physics_manager.em_parameters.pixe = True
sim.physics_manager.em_parameters.deexcitation_ignore_cut = True

## =============================
## == ACTORS                  ==
## =============================
stat = sim.add_actor("SimulationStatisticsActor", "Stats")
stat.output_filename = "stats_Gate10.txt"
hc = sim.add_actor('DigitizerHitsCollectionActor', 'Hits')
hc.attached_to = ['absorber']
hc.output_filename = 'CC_Gate10_Hits.root'
hc.attributes = gate_core.GateDigiAttributeManager.GetInstance().GetAvailableDigiAttributeNames()  # all available
hc.attributes = ['EventID', 'TrackID', 'ParentID', 'ParentParticleName', 'ParticleName', 'KineticEnergy',
                 'TotalEnergyDeposit', 'TrackCreatorProcess', 'ProcessDefinedStep']
# print(hc.attributes), sys.exit()

## =============================
## == VERBOSITY               ==
## =============================
sim.g4_verbose = False

## ============================
## ==  VISUALIZATION         ==
## ============================
sim.visu = True
# sim.visu_verbose = True
sim.visu_type = "qt" # default vrml
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
pandas.set_option('display.max_rows', 1000)
pandas.set_option('display.float_format', lambda x: f'{x:.3f}')
tree = uproot.open(sim.output_dir + '/' + hc.output_filename)['Hits']
print('\n =>', tree.num_entries, 'entries in tree Hits')
# print(tree.keys())
hits = tree.arrays(library='pd', entry_stop=None)  # None to read all entries
hits['TotalEnergyDeposit'] = hits['TotalEnergyDeposit'] * 1000  # keV
hits['KineticEnergy'] = hits['KineticEnergy'] * 1000  # keV
print(hits.to_string(index=False))
# print(hits[hits['ParticleName']=='gamma'].to_string(index=False))
print(pandas.Series(hits['ProcessDefinedStep'].to_numpy()).value_counts(normalize=True) * 100,
      '\n')  # !! entry_stop = None  !!
print(pandas.Series(hits['TrackCreatorProcess'].to_numpy()).value_counts(normalize=True) * 100,
      '\n')  # !! entry_stop = None  !!
