import os.path
import sys

import opengate_core
from opengate.managers import Simulation
from imaging.ComptonCamera_tests.Gate10.tools.analysis_basics import *
from imaging.ComptonCamera_tests.Gate10.allpix.allpix import *
from imaging.ComptonCamera_tests.Gate10.tools.analysis_pixelClusters import *
from imaging.ComptonCamera_tests.Gate10.tools.analysis_pixelHits import *
from opengate.geometry.volumes import *
from scipy.spatial.transform import Rotation as R
from imaging.ComptonCamera_tests.Gate10.tools.analysis_cones import *
from imaging.ComptonCamera_tests.tools.point_source_validation import *
from imaging.ComptonCamera_tests.tools.reconstruction import *

# TODO: how to visualize volume sources?
#  -> use mother volumes for box/sphere to help with visualization?
#  -> Or as in Gate9: /gate/source/source_name/visualize 1000 yellow 1

if __name__ == "__main__":
    sim, sim.output_dir = Simulation(), "output"
    um, mm, keV, MeV, deg, Bq, sec = g4_units.um, g4_units.mm, g4_units.keV, g4_units.MeV, g4_units.deg, g4_units.Bq, g4_units.s
    sim.volume_manager.add_material_database('../data/GateMaterials.db')
    sim.random_engine, sim.random_seed = "MersenneTwister", 6
    # sim.g4_verbose, sim.g4_verbose_level_tracking = True, 1  # useless if visu
    sim.visu = False

    # ===========================
    # ==   GEOMETRY            ==
    # ===========================
    npix, pitch, thickness = 6, 55 * um, 1 * mm
    sim.world.material = "Vacuum"
    # sim.world.color = [0] * 4
    sensor = sim.add_volume("Box", "sensor")
    sensor.material = "cadmium_telluride"
    sensor.size = [npix * pitch, npix * pitch, thickness]
    sensor.translation = [0 * um, 0 * um, 50 * mm]
    # sensor.rotation = R.from_euler('xyz', [0,90,0], degrees=True).as_matrix()
    # TODO: block below triggers 'WARNING Could not check overlap...' => problem?
    pixel = sim.add_volume("Box", "pixel")
    pixel.mother, pixel.size = sensor.name, [pitch, pitch, thickness]
    pixel.material = sensor.material
    par = RepeatParametrisedVolume(repeated_volume=pixel)
    par.linear_repeat, par.translation = [npix, npix, 1], [pitch, pitch, 0]
    sim.volume_manager.add_volume(par)

    ## ===========================
    ## ==  PHYSICS              ==
    ## ===========================
    doppler = True
    fluo = True
    if doppler: sim.physics_manager.physics_list_name = 'G4EmLivermorePhysics'
    if fluo:
        sim.physics_manager.global_production_cuts.gamma = 10 * um
        sim.physics_manager.global_production_cuts.electron = 10 * um
    sim.physics_manager.em_parameters.update(
        {'fluo': fluo, 'pixe': fluo, 'deexcitation_ignore_cut': False,
         'auger': fluo, 'auger_cascade': fluo})
    # TODO: impacts number of hits greatly, and depends if cuts were set or not

    ## =============================
    ## == ACTORS                  ==
    ## =============================
    hits = sim.add_actor('DigitizerHitsCollectionActor', 'Hits')
    hits.attached_to = sensor.name
    hits.authorize_repeated_volumes = True
    hits.attributes = opengate_core.GateDigiAttributeManager.GetInstance().GetAvailableDigiAttributeNames()
    # hits.keep_zero_edep = True # TODO compatible with gHits2cones_byEventID ?
    singles = sim.add_actor("DigitizerAdderActor", "Singles")
    singles.authorize_repeated_volumes = True
    singles.input_digi_collection = "Hits"
    singles.policy = "EnergyWeightedCentroidPosition"

    ## ============================
    ## == SOURCE                 ==
    ## ============================
    source = sim.add_source("GenericSource", "source")
    # source.n = 8
    source.activity, sim.run_timing_intervals = 10000 * Bq, [
        [0, 1 * sec]]  # ,[2 * sec, 3 * sec]]
    source.particle = "gamma"
    source.energy.mono = 140 * keV
    source.position.translation = [0 * mm, 0 * mm, 0 * mm]
    # source.position.type, source.position.radius = "sphere", 5 * mm
    # source.position.type, source.position.size = "box", [5 * mm] * 3
    # source.direction.theta, source.direction.phi = theta_phi(sensor, source)
    source.direction.type, source.direction.momentum = "momentum", [0, 0, 1]
    sim.world.size = get_worldSize(sensor, source, margin=5)

    ##=====================================================
    ##   RUN
    ##=====================================================

    hits.output_filename = 'hits_' + get_file_name(sim, doppler, fluo)
    singles.output_filename = 'singles_' + get_file_name(sim, doppler, fluo)
    sim.run(start_new_process=True)

    ##=====================================================
    ##   ANALYSIS
    ##=====================================================
    hits_path = sim.output_dir + '/' + hits.output_filename
    singles_path = sim.output_dir + '/' + singles.output_filename
    if not os.path.isfile(hits_path): sys.exit(f"{hits_path} does not exist")

    # BASICS
    # analyse_hits(hits_path)
    # analyse_singles(singles_path)
    # plot_hits_TotalEnergyDeposit(hits_path)
    # plot_hits_TotalEnergyDeposit_sumPerEvent(hits_path)

    # PIXEL HITS
    # 1) From singles
    pixelHits_singles = singles2pixelHits(singles_path)
    # print(pixelHits_singles.to_string(index=False))
    # plot_pixelHits_perEventID(pixelHits_singles, n_pixels=npix, log_scale=[False, False, False])
    # 2) From hits + allpix
    # run_allpix(sim, output_dir='allpix/', log_level='FATAL') # INFO, FATAL, ...
    # pixelHits_allpix = allpixTxt2pixelHit('allpix/data.txt',n_pixels=npix)
    # print(pixelHits_allpix.to_string(index=False))
    # # plot_pixelHits_comparison(pixelHits_singles,pixelHits_allpix,n_pixels=npix)
    # plot_pixelHits_comparison_perEventID(pixelHits_singles,pixelHits_allpix,n_pixels=npix,log_scale=[False, False, True])

    # PIXEL CLUSTERING
    clusters = pixelHits2pixelClusters(pixelHits_singles, npix)
    # print(clusters.to_string(index=False))

    # CONES TODO make it faster?
    # cones = gHits2cones_byEventID(hits_path, source.energy.mono, to_array=True)
    # # TODO cones = pixelClusters2cones(pixel_hits)

    # RECONSTRUCTION
    # name = hits.output_filename # TODO replace with pathlib.Path
    # l = name.replace("_", "\n").replace(".root",f'\n{cones.shape[0]} cones')
    # point_source_cone_validation(
    #     cones,
    #     vpitch=1,  # sim.world.size[2] / 256,
    #     source_pos=source.position.translation,
    #     plot_seq=False,
    #     plot_stack=True,
    #     plot_seq_napari=False,
    #     legend=l
    # )
    # reconstruct(cones,
    #             vsize=(256, 256, 256),
    #             vpitch=sim.world.size[2] / 256,
    #             output=hits_path.replace(".root", ".npy"),
    #             napari=True,
    #             detector={'size': sensor.size, 'position': sensor.translation}
    #             )
