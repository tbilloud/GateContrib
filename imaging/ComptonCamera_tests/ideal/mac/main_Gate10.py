# export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=2000000
import opengate as gate
import uproot

sim = gate.Simulation()
sim.output_dir = "../output"
sim.random_seed = 1

um = gate.g4_units.um
mm = gate.g4_units.mm
keV = gate.g4_units.keV
MeV = gate.g4_units.MeV
deg = gate.g4_units.deg

## ===========================
## == LOAD DATABASE         ==
## ===========================
sim.volume_manager.add_material_database('../../data/GateMaterials.db')

# ===========================
# ==   GEOMETRY            ==
# ===========================
#======== World=================
sim.world.material = "Vacuum"
sim.world.size = [200 * mm, 200 * mm, 200 * mm]
sensor_side = 14 * mm
BB = sim.add_volume("Box", "BB")
BB.size = [sensor_side, sensor_side, 2 * mm]
BB.material = "Vacuum"
BB.translation = [0 * mm, 0 * mm, 10 * mm]
absorber = sim.add_volume("Box", "absorber")
absorber.mother = BB.name
absorber.size = [sensor_side, sensor_side, 1 * mm]
absorber.translation = [0 * mm, 0 * mm, 0.5 * mm]
absorber.material = "CdTe"


## ===========================
## ==  PHYSICS              ==
## ===========================
sim.physics_manager.physics_list_name = "G4EmLivermorePhysics"
sim.physics_manager.set_production_cut("absorber", "electron", 10 * um)
sim.physics_manager.set_production_cut("absorber", "positron", 10 * um)
# sim.physics_manager.energy_range_min = 10 * eV
# sim.physics_manager.energy_range_max = 1 * MeV

## =============================
## == ACTORS                  ==
## =============================
stat = sim.add_actor("SimulationStatisticsActor", "Stats")
stat.output_filename = "stats_Gate10.txt"
#/gate/actor/addActor  ComptonCameraActor                CC_digi_BB
#/gate/actor/CC_digi_BB/attachTo                         BB
#/gate/actor/CC_digi_BB/save                             {out}/CC.root
#/gate/actor/CC_digi_BB/saveHitsTree                     1
#/gate/actor/CC_digi_BB/saveSinglesTree                  1
#/gate/actor/CC_digi_BB/saveCoincidencesTree             1
#/gate/actor/CC_digi_BB/saveCoincidenceChainsTree        1
#/gate/actor/CC_digi_BB/saveEventInfoTree                1
#/gate/actor/CC_digi_BB/absorberSDVolume                 absorber
#/gate/actor/CC_digi_BB/scattererSDVolume                scatterer
#/gate/actor/CC_digi_BB/numberOfTotScatterers            1
#/gate/actor/CC_digi_BB/specifysourceParentID            0
#/gate/digitizer/layers/insert adderComptPhotIdeal # WARNING: validated using livermore physics list.
#/gate/digitizer/Coincidences/setWindow 50 ns
#/gate/digitizer/Coincidences/setAcceptancePolicy4CC keepAll
#/gate/digitizer/name sequenceCoincidence
#/gate/digitizer/insert coincidenceChain
#/gate/digitizer/sequenceCoincidence/addInputName Coincidences
#/gate/digitizer/sequenceCoincidence/insert sequenceRecon
#/gate/digitizer/sequenceCoincidence/sequenceRecon/setSequencePolicy singlesTime # axialDist2Source
hc = sim.add_actor('DigitizerHitsCollectionActor', 'Hits')
hc.attached_to = ['absorber']
hc.output_filename = 'CC_Gate10_Hits.root'
hc.attributes = ['TotalEnergyDeposit', 'KineticEnergy', 'PostPosition', 'GlobalTime', 'RunID', 'TrackID']

## =============================
## == VERBOSITY               ==
## =============================
#/process/em/verbose 0 # reduces the console output a lot !
#/vis/verbose errors # reduces the console output
sim.g4_verbose = True

## ============================
## ==  VISUALIZATION         ==
## ============================
# sim.visu = True
# sim.visu_type = "qt"

## ============================
## == SOURCE                 ==
## ============================
source = sim.add_source("GenericSource","source_point")
source.particle = "gamma"
source.energy.mono = 140 * keV
source.direction.type = 'momentum'
source.direction.momentum = [0,0,1]

##====================================================
##  R A N D O M   E N G I N E  A N D  S E E D
##====================================================
sim.random_engine = "MersenneTwister"

##=====================================================
##   M E A S U R E M E N T   S E T T I N G S
##=====================================================
source.n = 100
sim.run()

##=====================================================
##   ANALYSIS
##=====================================================
tree = uproot.open(sim.output_dir+'/'+hc.output_filename)['Hits']
print('\n =>', tree.num_entries, 'entries in tree Hits')
print(tree.keys())
hits = tree.arrays(library='pd', entry_stop=None)  # None to read all entries


import opengate_core as gate_core
am = gate_core.GateDigiAttributeManager.GetInstance()
print(am.GetAvailableDigiAttributeNames())
