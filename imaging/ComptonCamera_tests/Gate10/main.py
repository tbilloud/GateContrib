import sys
import cupy as cp
import opengate_core
from opengate.utility import g4_units
from opengate.managers import Simulation
from imaging.ComptonCamera_tests.Gate10.tools.analysis_basics import *
from imaging.ComptonCamera_tests.Gate10.allpix.allpix import *
from imaging.ComptonCamera_tests.Gate10.tools.analysis_pixelClusters3 import *
from imaging.ComptonCamera_tests.Gate10.tools.analysis_pixelHits import *
from imaging.ComptonCamera_tests.Gate10.tools.utils import *
from imaging.ComptonCamera_tests.tools.point_source_validation import *
from imaging.ComptonCamera_tests.tools.reconstruction import *
from opengate.geometry.volumes import *
from scipy.spatial.transform import Rotation as R

if __name__ == "__main__":
    sim, sim.output_dir = Simulation(), "output"
    um, mm, keV, MeV, deg, Bq, sec = g4_units.um, g4_units.mm, g4_units.keV, g4_units.MeV, g4_units.deg, g4_units.Bq, g4_units.s
    sim.volume_manager.add_material_database('../data/GateMaterials.db')
    sim.random_engine, sim.random_seed = "MersenneTwister", 1
    # sim.g4_verbose, sim.g4_verbose_level_tracking = True, 1  # useless if visu
    sim.visu = True

    # ===========================
    # ==   GEOMETRY            ==
    # ===========================
    npix, pitch, thickness = 10, 55 * um, 1 * mm
    sim.world.material = "Vacuum"
    sim.world.size = [10 * mm] * 3
    # sim.world.color = [0] * 4
    sensor = sim.add_volume("Box", "sensor")
    sensor.material = "cadmium_telluride"
    sensor.size = [npix * pitch, npix * pitch, thickness]
    sensor.translation = [0 * mm, 0 * mm, 1 * mm]
    sensor.rotation = R.from_euler('y', 45, degrees=True).as_matrix()
    # if not sim.visu: # TODO add this when using many pixels
    # TODO: WARNING Could not check overlap for volume ... => problem?
    pixel = sim.add_volume("Box", "pixel")
    pixel.mother, pixel.size = sensor.name, [pitch, pitch, thickness]
    pixel.material = sensor.material # TODO necessary?
    # pixel
    par = RepeatParametrisedVolume(repeated_volume=pixel)
    par.linear_repeat, par.translation = [npix, npix, 1], [pitch, pitch, 0]
    sim.volume_manager.add_volume(par)

    ## ===========================
    ## ==  PHYSICS              ==
    ## ===========================
    doppler = False
    fluo = True
    if doppler: sim.physics_manager.physics_list_name = 'G4EmLivermorePhysics'
    if fluo: sim.physics_manager.global_production_cuts.all = 10 * um
    sim.physics_manager.em_parameters.update(
        {'fluo': fluo, 'pixe': fluo, 'deexcitation_ignore_cut': False,
         'auger': fluo, 'auger_cascade': fluo})
    # TODO: impacts number of hits greatly, and depends if cuts were set or not

    ## =============================
    ## == ACTORS                  ==
    ## =============================
    # HITS
    hits = sim.add_actor('DigitizerHitsCollectionActor', 'Hits')
    hits.attached_to = sensor.name
    hits.authorize_repeated_volumes = True # TODO required (doc), but useless
    hits.attributes = opengate_core.GateDigiAttributeManager.GetInstance().GetAvailableDigiAttributeNames()
    # SINGLES
    singles = sim.add_actor("DigitizerAdderActor", "Singles")
    singles.input_digi_collection = "Hits"
    singles.policy = "EnergyWeightedCentroidPosition"
    singles.output_filename = 'CC_Singles.root'  # if hc.output_filename, there will be two branches in the file
    # INTEGRATED HIT FRAME
    proj = sim.add_actor("DigitizerProjectionActor", "Projection")
    proj.input_digi_collections = ["Singles"]
    proj.authorize_repeated_volumes = True
    proj.spacing = [pitch, pitch]
    proj.size = [npix, npix]
    proj.output_filename = 'projection.mhd'

    ## ============================
    ## == SOURCE                 ==
    ## ============================
    source = sim.add_source("GenericSource", "source")
    source.particle = "proton"
    source.energy.mono = 1000 * MeV
    source.position.translation = [0 * mm, 0 * mm, -1 * mm]
    # source.position.type, source.position.radius = "sphere", 5 * mm
    # source.position.type, source.position.size = "box", [5 * mm] * 3
    # TODO: use mother volumes for box/sphere to help with visualization?
    # source.direction.theta, source.direction.phi = theta_phi(sensor, source)
    source.direction.type, source.direction.momentum = "momentum", [0, 0, 1]
    # sim.world.size = get_worldSize(sensor, source)

    ##=====================================================
    ##   M E A S U R E M E N T
    ##=====================================================
    source.n = 1
    # source.activity, sim.run_timing_intervals = 100 * Bq, [[0, 2 * sec]] #,[2 * sec, 3 * sec]]
    events = f'{source.n}events' if source.n else f'{int(source.activity / Bq)}Bq_{int(sum_time_intervals(sim.run_timing_intervals)) / sec}sec'
    hits.output_filename = f'source{source.energy.mono}MeV_{events}_doppler{doppler}_fluo{fluo}.root'
    sim.run()

    ##=====================================================
    ##   ANALYSIS
    ##=====================================================
    hits_path = sim.output_dir + '/' + hits.output_filename
    singles_path = sim.output_dir + '/' + singles.output_filename

    # BASICS
    analyse_hits(hits_path)
    analyse_singles(singles_path)
    plot_DigitizerProjectionActor(sim)
    # plot_hits_TotalEnergyDeposit(hits_path)
    # plot_hits_TotalEnergyDeposit_sumPerEvent(hits_path)

    # PIXEL HITS
    # 1) From singles
    pixelHits = singles2pixelHits(singles_path)  # Gate
    print(pixelHits.to_string(index=False))
    # plot_pixelHits_byEventID(pixelHits, eventID=0, n_pixels=npix)
    # # 2) From hits + allpix
    # run_allpix(sim, output_dir='allpix/', log_level='FATAL') # log_level can be INFO, FATAL
    # pixelHits = allpixTxt2pixelHit('allpix/data.txt')
    # # save_pixelHits_burdaman_format(pixelHits, output_path=hits_path.replace(".root", ".txt"))
    # print(pixelHits.to_string(index=False))
    # # plot_pixelHits_byEventID(pixelHits, eventID=0, n_pixels=npix)

    # PIXEL CLUSTERING
    clusters = pixelHits2pixelClusters(pixelHits)
    print(clusters)
    # TODO pixelClusters = pixelHits2pixelClusters
    # TODO coincidences = pixelClusters2coincidences
    # TODO cones = coincidences2cones(pixel_hits)

    sys.exit()

    # CONES
    # ### IDEAL ###
    # cones = gHits2cones_byEventID(hits_path, source.energy.mono, to_array=True) # TODO make it faster
    # print(c)
    print('=>', cones.shape[0] if cones.shape[0] else sys.exit('No cones'),
          'cones,', cp.isnan(cones).any(axis=1).sum(),
          'with NaNs')

    # RECONSTRUCTION
    # Point source validation
    point_source_cone_validation(cones,
                                 world_z=sim.world.size[2],
                                 source_pos=source.position.translation,
                                 plot_seq=False,
                                 plot_stack=True,
                                 plot_seq_napari=False,
                                 legend=hits.output_filename.replace("_",
                                                                     "\n").replace(
                                     ".root",
                                     f'\n{cones.shape[0]} cones'),
                                 )
    # Image reconstruction
    reconstruct(cones,
                vsize=(256, 256, 256),
                vpitch=sim.world.size[2] / 256,
                output=hits_path.replace(".root", ".npy"),
                napari=True,
                detector={'size': sensor.size, 'position': sensor.translation}
                )
