import sys
import cupy as cp
import opengate_core
from opengate.utility import g4_units
from opengate.managers import Simulation
from imaging.ComptonCamera_tests.Gate10.tools.analysis_basics import analyse_hits
from imaging.ComptonCamera_tests.Gate10.allpix.allpix import run_allpix, allpixTxt2pixelHit
from imaging.ComptonCamera_tests.Gate10.tools.analysis_pixelHits import plot_pixelHits_byEventID, singles2pixelHits
from imaging.ComptonCamera_tests.tools.point_source_validation import point_source_cone_validation
from imaging.ComptonCamera_tests.tools.reconstruction import reconstruct
from opengate.geometry.volumes import RepeatParametrisedVolume

if __name__ == "__main__":
    sim, sim.output_dir = Simulation(), "output"
    um, mm, keV, MeV, deg, Bq, sec = g4_units.um, g4_units.mm, g4_units.keV, g4_units.MeV, g4_units.deg, g4_units.Bq, g4_units.s

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
    npix, pitch, thickness = 256, 55 * um, 1 * mm
    sim.world.material = "Vacuum"
    sim.world.size = [npix * pitch + 1, npix * pitch + 1, thickness * 2 + 1]  # + 1 avoids segmentation fault
    sensor = sim.add_volume("Box", "sensor")
    sensor.material = "cadmium_telluride"
    sensor.size = [npix * pitch, npix * pitch, thickness]
    sensor.translation = [0 * mm, 0 * mm, thickness / 2]
    # sensor.rotation = R.from_euler('z', 45, degrees=True).as_matrix()
    # TODO: WARNING Could not check overlap for volume pixel_param. => problem?
    if not sim.visu:
        pixel = sim.add_volume("Box", "pixel")
        pixel.mother, pixel.material, pixel.size = sensor.name, 'cadmium_telluride', [pitch, pitch, thickness]
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
    # HITS
    hits = sim.add_actor('DigitizerHitsCollectionActor', 'Hits')
    hits.attached_to = sensor.name
    # hits.authorize_repeated_volumes = True  # required according to doc, but seems useless
    hits.attributes = opengate_core.GateDigiAttributeManager.GetInstance().GetAvailableDigiAttributeNames()
    # SINGLES
    singles = sim.add_actor("DigitizerAdderActor", "Singles")
    singles.input_digi_collection = "Hits"
    singles.policy = "EnergyWeightedCentroidPosition"
    singles.output_filename = 'CC_Singles.root'  # if hc.output_filename, there will be two branches in the file
    # # TIMEPIX FRAME
    # proj = sim.add_actor("DigitizerProjectionActor", "Projection")
    # proj.input_digi_collections = ["Singles"]
    # proj.spacing = [pitch, pitch]  # Set pixel spacing in mm
    # proj.size = [npix, npix]  # Image size in pixels (128x128)
    # proj.output_filename = 'projection.mhd'

    ## =============================
    ## == VERBOSITY               ==
    ## =============================
    # sim.g4_verbose, sim.g4_verbose_level_tracking = True, 1  # not working if visualization

    ## ============================
    ## == SOURCE                 ==
    ## ============================
    source = sim.add_source("GenericSource", "source")
    source.particle = "gamma"
    source.energy.mono = 100 * keV
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
    # source.n = 1
    source.activity, sim.run_timing_intervals = 10 * Bq, [[0, 1 * sec]]
    events = f'{source.n}events' if source.n else f'{int(source.activity/Bq)}Bq_{int(sim.run_timing_intervals[0][1]/sec)}sec'
    hits.output_filename = f'MeV{source.energy.mono}_{events}_doppler{doppler}_fluo{fluo}.root'
    sim.run()

    ##=====================================================
    ##   ANALYSIS
    ##=====================================================
    hits_path = sim.output_dir + '/' + hits.output_filename
    singles_path = sim.output_dir + '/' + singles.output_filename

    # Basics
    analyse_hits(hits_path)
    # analyse_singles(sim.output_dir + '/' + sc.output_filename)
    # plot_DigitizerProjectionActor(sim)
    # plot_hits_TotalEnergyDeposit(hits_path)
    # plot_hits_TotalEnergyDeposit_sumPerEvent(hits_path)

    # Pixel hits
    # ### From singles ###
    pixelHits = singles2pixelHits(singles_path) # Gate
    print(pixelHits.to_string(index=False))
    # plot_pixelHits_byEventID(pixelHits, eventID=0, n_pixels=npix)
    # ### From hits + allpix ###
    run_allpix(sim, output_dir='allpix/', log_level='FATAL') # log_level can be INFO, FATAL
    pixelHits = allpixTxt2pixelHit('allpix/data.txt')
    # save_pixelHits_burdaman_format(pixelHits, output_path=hits_path.replace(".root", ".txt"))
    print(pixelHits.to_string(index=False))
    # plot_pixelHits_byEventID(pixelHits, eventID=0, n_pixels=npix)
    # TODO pixelClusters = pixelHits2pixelClusters
    # TODO coincidences = pixelClusters2coincidences
    # TODO cones = coincidences2cones(pixel_hits)

    # Cones
    # ### IDEAL ###
    # cones = gHits2cones_byEventID(hits_path, source.energy.mono, to_array=True) # TODO make it faster

    sys.exit()

    # print(c)
    print('=>', cones.shape[0] if cones.shape[0] else sys.exit('No cones'), 'cones,', cp.isnan(cones).any(axis=1).sum(), 'with NaNs')

    # Point source validation
    point_source_cone_validation(cones,
                                 world_z=sim.world.size[2],
                                 source_pos=source.position.translation,
                                 plot_seq=False,
                                 plot_stack=True,
                                 plot_seq_napari=False,
                                 legend=hits.output_filename.replace("_", "\n").replace(".root", f'\n{cones.shape[0]} cones'),
                                 )

    # Image reconstruction
    reconstruct(cones,
                vsize=(256, 256, 256),
                vpitch=sim.world.size[2] / 256,
                output= hits_path.replace(".root", ".npy"),
                napari=True,
                detector={'size': sensor.size, 'position': sensor.translation}
                )
