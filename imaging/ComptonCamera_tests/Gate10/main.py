import sys
import cupy as cp
import opengate as gate, opengate_core
import imaging.ComptonCamera_tests.Gate10.tools.analysis_basics as analysis_basics
from imaging.ComptonCamera_tests.Gate10.tools.analysis_cones import hits2cones_byEventID
from imaging.ComptonCamera_tests.tools.point_source_validation import point_source_cone_validation
from imaging.ComptonCamera_tests.tools.reconstruction import reconstruct

sim, sim.output_dir = gate.Simulation(), "output"
um, mm, keV, MeV, deg = gate.g4_units.um, gate.g4_units.mm, gate.g4_units.keV, gate.g4_units.MeV, gate.g4_units.deg

## ===========================
## == LOAD DATABASE         ==
## ===========================
sim.volume_manager.add_material_database('../data/GateMaterials.db')

# ===========================
# ==   GEOMETRY            ==
# ===========================
npix, pitch, thickness = 1000, 55 * um, 100 * mm
sim.world.material = "Vacuum"
sim.world.size = [npix * pitch + 1, npix * pitch + 1, thickness * 2 + 1]  # + 1 avoids segmentation fault
sensor = sim.add_volume("Box", "sensor")
sensor.material = "CdTe"
sensor.size = [npix * pitch, npix * pitch, thickness]
sensor.translation = [0 * mm, 0 * mm, thickness / 2]
# sensor.rotation = R.from_euler('z', 45, degrees=True).as_matrix()
# pixel = sim.add_volume("Box", "pixel")
# pixel.mother, pixel.material, pixel.size = sensor.name, 'Tungsten', [pitch, pitch, thickness]
# pixel.translation = gate.geometry.utility.get_grid_repetition([int(npix * pitch / pitch)] * 2 + [1], [pitch, pitch, 0])
# # pixel.color = [0, 0, 0, 0]  # see trajectories better

## ===========================
## ==  PHYSICS              ==
## ===========================
doppler = False
fluo = True
if doppler: sim.physics_manager.physics_list_name = 'G4EmLivermorePhysics'
if fluo: sim.physics_manager.global_production_cuts.all = 10 * um
sim.physics_manager.em_parameters.update(
    {'fluo': fluo,
     'pixe': fluo,
     'deexcitation_ignore_cut': False,  # TODO: impacts number of hits greatly, and depends if cuts were set or not
     'auger': fluo, 'auger_cascade': fluo})

## =============================
## == ACTORS                  ==
## =============================
hits = sim.add_actor('DigitizerHitsCollectionActor', 'Hits')
hits.attached_to = sensor.name
# hc.authorize_repeated_volumes = True  # required according to doc, but seems useless
hits.output_filename = 'CC_Hits.root'
hits.attributes = opengate_core.GateDigiAttributeManager.GetInstance().GetAvailableDigiAttributeNames()

## =============================
## == VERBOSITY               ==
## =============================
# sim.g4_verbose, sim.g4_verbose_level_tracking = True, 1  # not working if visualization

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
source.direction.type, source.direction.theta, source.direction.phi = "iso", [160 * deg, 180 * deg], [0, 360 * deg]
# source.direction.type, source.direction.momentum = "momentum", [0, 0, 1]
source.position.translation = [0 * mm, 0 * mm, -thickness / 2]

##====================================================
##  R A N D O M   E N G I N E  A N D  S E E D
##====================================================
sim.random_engine, sim.random_seed = "MersenneTwister", 1

##=====================================================
##   M E A S U R E M E N T
##=====================================================
source.n = 810
# source.activity = 1000 * gate.g4_units.Bq # for sorting coincidences with GlobalTime
sim.run()

##=====================================================
##   ANALYSIS
##=====================================================
hits_path = sim.output_dir + '/' + hits.output_filename

# Basics
# analysis_basics.analyse_hits(hits_path), sys.exit()
# analysis.analyse_singles(sim.output_dir + '/' + sc.output_filename)
# plot_DigitizerProjectionActor(sim)
# analysis_basics.plot_hits_TotalEnergyDeposit(hits_path)
# analysis_basics.plot_hits_TotalEnergyDeposit_sumPerEvent(hits_path)
# sys.exit()

# Cones
c = hits2cones_byEventID(hits_path, source.energy.mono)
print('=>', c.shape[0] if c.shape[0] else sys.exit('No cones'), 'cones,', cp.isnan(c).any(axis=1).sum(), 'with NaNs')
point_source_cone_validation(c, sim.world.size[2], source.position.translation,
                             plot_seq=False, plot_stack=True)

# Image reconstruction
name = f'fluo{fluo}_doppler{doppler}'
reconstruct(c, (256, 256, 256), sim.world.size[2] / 256, output=f'output/reco_{name}.npy')
