import sys
import cupy as cp
import opengate_core
from opengate.utility import g4_units
from opengate.managers import Simulation
from imaging.ComptonCamera_tests.Gate10.tools.analysis_basics import analyse_hits
from imaging.ComptonCamera_tests.Gate10.tools.analysis_cones import hits2cones_byEventID
from imaging.ComptonCamera_tests.tools.point_source_validation import point_source_cone_validation
from imaging.ComptonCamera_tests.tools.reconstruction import reconstruct
from opengate.geometry.volumes import RepeatParametrisedVolume, BoxVolume

sim, sim.output_dir = Simulation(), "output"
um, mm, keV, MeV, deg = g4_units.um, g4_units.mm, g4_units.keV, g4_units.MeV, g4_units.deg

## ===========================
## == LOAD DATABASE         ==
## ===========================
sim.volume_manager.add_material_database('../data/GateMaterials.db')

## ============================
## ==  VISUALIZATION         ==
## ============================
sim.visu = False  # defaults to vrml, qt seems to not work on ubuntu yet

# ===========================
# ==   GEOMETRY            ==
# ===========================
npix, pitch, thickness = 256, 55 * um, 10 * mm
sim.world.material = "Vacuum"
sim.world.size = [npix * pitch + 1, npix * pitch + 1, thickness * 2 + 1]  # + 1 avoids segmentation fault
sensor = sim.add_volume("Box", "sensor")
sensor.material = "CdTe"
sensor.size = [npix * pitch, npix * pitch, thickness]
sensor.translation = [0 * mm, 0 * mm, thickness / 2]
# sensor.rotation = R.from_euler('z', 45, degrees=True).as_matrix()
# TODO: WARNING Could not check overlap for volume pixel_param. => problem?
if not sim.visu:
    pixel = sim.add_volume("Box", "pixel")
    pixel.mother, pixel.material, pixel.size = sensor.name, 'CdTe', [pitch, pitch, thickness]
    pixelp = RepeatParametrisedVolume(repeated_volume=pixel)
    pixelp.linear_repeat, pixelp.translation = [npix, npix, 1], [pitch, pitch, 0]
    sim.volume_manager.add_volume(pixelp)
    # pixel.color = [0, 0, 0, 0]  # see trajectories better

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
# hits.authorize_repeated_volumes = True  # required according to doc, but seems useless
hits.attributes = opengate_core.GateDigiAttributeManager.GetInstance().GetAvailableDigiAttributeNames()

## =============================
## == VERBOSITY               ==
## =============================
# sim.g4_verbose, sim.g4_verbose_level_tracking = True, 1  # not working if visualization

## ============================
## == SOURCE                 ==
## ============================
source = sim.add_source("GenericSource", "source")
source.particle = "gamma"
source.energy.mono = 200 * keV
# source.position.type, source.position.radius = "sphere", 10 * mm
source.position.type, source.position.size = "box", [5 * mm, 5 * mm, 5 * mm]
# source.direction.type, source.direction.theta, source.direction.phi = "iso", [160 * deg, 180 * deg], [0, 360 * deg]
# TODO: use mother volumes for box/sphere to help with visualization?
# source.direction.type, source.direction.momentum = "momentum", [0, 0, 1]
source.position.translation = [0 * mm, 0 * mm, -thickness / 2]

##====================================================
##  R A N D O M   E N G I N E  A N D  S E E D
##====================================================
sim.random_engine, sim.random_seed = "MersenneTwister", 1

##=====================================================
##   M E A S U R E M E N T
##=====================================================
source.n = 1000000
# source.activity = 1000 * gate.g4_units.Bq # for sorting coincidences with GlobalTime
hits.output_filename = f'MeV{source.energy.mono}_events{source.n}_doppler{doppler}_fluo{fluo}.root'
sim.run()

##=====================================================
##   ANALYSIS
##=====================================================
hits_path = sim.output_dir + '/' + hits.output_filename

# Basics
# analyse_hits(hits_path)
# analyse_singles(sim.output_dir + '/' + sc.output_filename)
# plot_DigitizerProjectionActor(sim)
# plot_hits_TotalEnergyDeposit(hits_path)
# plot_hits_TotalEnergyDeposit_sumPerEvent(hits_path)

# Cones
# TODO much slower than simulation time...
c = hits2cones_byEventID(hits_path, source.energy.mono, to_array=True)
# print(c)
print('=>', c.shape[0] if c.shape[0] else sys.exit('No cones'), 'cones,', cp.isnan(c).any(axis=1).sum(), 'with NaNs')

# Point source validation
point_source_cone_validation(c,
                             world_z=sim.world.size[2],
                             source_pos=source.position.translation,
                             plot_seq=False,
                             plot_stack=True,
                             plot_seq_napari=False,
                             legend=hits.output_filename.replace("_", "\n").replace(".root", f'\n{c.shape[0]} cones'),
                             )

# Image reconstruction
reconstruct(c,
            vsize=(256, 256, 256),
            vpitch=sim.world.size[2] / 256,
            output= hits_path.replace(".root", ".npy"),
            napari=True,
            detector={'size': sensor.size, 'position': sensor.translation}
            )
