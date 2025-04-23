import sys
import opengate_core
from opengate.managers import Simulation
from opengate.geometry.volumes import *
from tools.analysis_pixelClusters import *
from tools.point_source_validation import *
from tools.reco_backprojection import *
from tools.allpix import *

if __name__ == "__main__":
    sim, sim.output_dir = Simulation(), "output"
    um, mm, keV, MeV, deg, Bq, ms, sec = g4_units.um, g4_units.mm, g4_units.keV, g4_units.MeV, g4_units.deg, g4_units.Bq, g4_units.ms, g4_units.s
    sim.volume_manager.add_material_database('../data/GateMaterials.db')
    sim.random_engine, sim.random_seed = "MersenneTwister", 1
    sim.visu = False
    # sim.g4_verbose, sim.g4_verbose_level_tracking = True, 1  # useless if visu
    # sim.verbose_level = 'DEBUG'

    # ===========================
    # ==   GEOMETRY            ==
    # ===========================
    npix, pitch, thickness = 256, 55 * um, 1 * mm
    sim.world.material = "Vacuum"
    sensor = sim.add_volume("Box", "sensor")
    sensor.material = "cadmium_telluride"
    sensor.size = [npix * pitch, npix * pitch, thickness]
    sensor.translation = [0 * mm, 0 * mm, 5 * mm]
    # sensor.rotation = R.from_euler('xyz', [0,45,0], degrees=True).as_matrix()
    if not sim.visu:
        pixel = sim.add_volume("Box", "pixel")
        pixel.mother, pixel.size = sensor.name, [pitch, pitch, thickness]
        pixel.material = sensor.material
        par = RepeatParametrisedVolume(repeated_volume=pixel)
        par.linear_repeat, par.translation = [npix, npix, 1], [pitch, pitch, 0]
        sim.volume_manager.add_volume(par)

    ## ===========================
    ## ==  PHYSICS              ==
    ## ===========================
    doppler = False
    fluo = False
    if doppler: sim.physics_manager.physics_list_name = 'G4EmLivermorePhysics'
    if fluo:
        sim.physics_manager.global_production_cuts.gamma = 1 * um
        sim.physics_manager.global_production_cuts.electron = 100 * um
    sim.physics_manager.em_parameters.update(
        {'fluo': fluo, 'pixe': fluo, 'deexcitation_ignore_cut': False,
         'auger': fluo, 'auger_cascade': fluo})
    # TODO: deexcitation_ignore_cut impacts number of hits, and depends on cuts

    ## =============================
    ## == ACTORS                  ==
    ## =============================
    hits = sim.add_actor('DigitizerHitsCollectionActor', 'Hits')
    hits.attached_to = sensor.name
    hits.authorize_repeated_volumes = True
    hits.attributes = opengate_core.GateDigiAttributeManager.GetInstance().GetAvailableDigiAttributeNames()
    hits.output_filename = 'hits.root'
    # hits.keep_zero_edep = True # TODO compatible with gHits2cones_byEventID ?

    ## ============================
    ## == SOURCE                 ==
    ## ============================
    source = sim.add_source("GenericSource", "source")
    source.n = 100
    # source.activity, sim.run_timing_intervals = 100_000 * Bq, [[0, 2 * ms]]
    source.particle = "gamma"
    source.energy.mono = 100 * keV
    source.position.translation = [0 * mm, 0 * mm, -5 * mm]
    source.direction.type, source.direction.momentum = "momentum", [0, 0, 1]
    # source.direction.theta, source.direction.phi = theta_phi(sensor, source)
    sim.world.size = get_worldSize(sensor, source, margin=10)

    ## ============================
    ## ==  RUN                   ==
    ## ============================
    sim.run()

    ## ============================
    ## ==  OFFLINE ANALYSIS      ==
    ## ============================
    # TODO adapt to multiple sim runs
    hits_path = Path(sim.output_dir) / hits.output_filename
    hits_df = uproot.open(hits_path)['Hits'].arrays(library='pd')
    print_hits_inG4format(hits_df[hits_df['EventID']==96])

    # ################# PIXEL HITS ########################
    pixelHits = gHits2allpix2pixelHits(sim, npix, config='fast')
    # pixelHits[TOA] = pixelHits.groupby(EVENTID)[TOA].transform(lambda x: x - x.min())
    if source.n: pixelHits[TOA] += pixelHits.groupby(EVENTID).ngroup() * 1000
    # TODO include above line in gHits2allpix2pixelHits or pixelHits2pixelClusters?
    print(pixelHits[pixelHits['EventID'] == 96])

    # ################# PIXEL CLUSTERS ####################
    pixelClusters = pixelHits2pixelClusters(pixelHits, npix=npix,
                                            window_ns=100,
                                            func='method2',
                                            pitch_um=pitch * 1000)
    print(pixelClusters[pixelClusters['EventID'] == 96])

    # #################### CONES ##########################
    # =======> GROUND TRUTH <=======
    cones_truth = gHits2cones_byEvtID(hits_path, source.energy.mono)
    # print_hits_gammas(hits_df[hits_df['EventID'].isin(eventIDs)])
    # print(pixelHits[pixelHits[id].isin(eventIDs)])
    cones_truth = cones_truth[cones_truth['EventID'] != 91]
    print(cones_truth)
    # =========> TIMEPIX <==========
    # eventIDs = cones_truth['EventID'].unique()
    cones_tpx = pixelClusters2cones_byEvtID(pixelClusters,
                                            source_MeV=source.energy.mono,
                                            thickness_um=thickness * 1000)
    cones_tpx_simuCoord = tpxCones2simuCoordinates(cones_tpx, sensor)
    print(cones_tpx_simuCoord)

    # ################## RECONSTRUCTION ####################
    sp, vp, vs = source.position.translation, 0.1, (256, 256, 256)
    validate_psource(cones_truth, source_pos=sp, vpitch=vp, vsize=vs,
                     plot_seq=False, plot_stack=True, plot_napari=False)
    validate_psource(cones_tpx_simuCoord, source_pos=sp, vpitch=vp, vsize=vs,
                     plot_seq=False, plot_stack=True, plot_napari=False)
