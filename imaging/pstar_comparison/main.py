# Script to analyse energy deposits of protons in silicon, to compare with pstar values:
# https://physics.nist.gov/PhysRefData/Star/Text/PSTAR.html

# For fitting landau curves (last code block):
# -> ROOT must be installed and activated by running 'source /path/thisroot.sh'
# -> Run script from terminal: python -i main.py

import sys

import matplotlib.pyplot as plt
import uproot
from opengate.utility import g4_units
from opengate.managers import Simulation
import opengate_core
from pandas import Series

if __name__ == "__main__":
    sim, sim.output_dir = Simulation(), "output"
    um, mm, keV, MeV, deg, Bq, sec = g4_units.um, g4_units.mm, g4_units.keV, g4_units.MeV, g4_units.deg, g4_units.Bq, g4_units.s
    sim.volume_manager.add_material_database('GateMaterials.db')

    ## =============================
    ## = VISUALIZATION / VERBOSITY =
    ## =============================
    sim.visu = False  # proton = blue, e- = red, gamma = green, e+ = yellow?
    # sim.g4_verbose, sim.g4_verbose_level_tracking = True, 1  # not working if visualization

    # ===========================
    # ==   GEOMETRY            ==
    # ===========================
    thickness = 10000 * um
    sim.world.material = "Vacuum"
    sim.world.size = [thickness * 1.01, thickness * 1.01, thickness * 2.01]
    sensor = sim.add_volume("Box", "sensor")
    sensor.material = "Silicon"
    sensor.size = [thickness, thickness, thickness]
    sensor.translation = [0 * mm, 0 * mm, thickness / 2]

    ## =============================
    ## == ACTORS                  ==
    ## =============================
    hits = sim.add_actor('DigitizerHitsCollectionActor', 'Hits')
    hits.attached_to = sensor.name
    hits.attributes = opengate_core.GateDigiAttributeManager.GetInstance().GetAvailableDigiAttributeNames()
    hits.output_filename = f'hits.root'
    singles = sim.add_actor("DigitizerAdderActor", "Singles")
    singles.input_digi_collection = "Hits"
    singles.policy = "EnergyWeightedCentroidPosition"
    singles.output_filename = 'singles.root'  # if hc.output_filename, there will be two branches in the file

    ##====================================================
    ##  R A N D O M   E N G I N E  A N D  S E E D
    ##====================================================
    sim.random_engine, sim.random_seed = "MersenneTwister", 1

    ## ============================
    ## == SOURCE                 ==
    ## ============================
    source = sim.add_source("GenericSource", "source")
    source.particle = "proton"
    source.energy.mono = 1000 * MeV
    source.direction.type, source.direction.momentum = "momentum", [0, 0, 1]

    ## ===========================
    ## ==  PHYSICS              ==
    ## ===========================
    # sim.physics_manager.physics_list_name = 'G4EmLivermorePhysics'
    # sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4" # removes 'hadElastic' processes
    sim.physics_manager.global_production_cuts.all = 1e99 * mm

    ##=====================================================
    ##   M E A S U R E M E N T
    ##=====================================================
    source.n = 10000
    sim.run()

    ##=====================================================
    ##   ANALYSIS
    ##=====================================================
    hits_path = sim.output_dir + '/' + hits.output_filename
    singles_path = sim.output_dir + '/' + singles.output_filename

    # Check processes
    hits = uproot.open(hits_path)['Hits'].arrays(library='pd')
    # print(hits[['EventID','ProcessDefinedStep','TrackID', 'ParticleName', 'ParentID','TotalEnergyDeposit']])
    print(Series(hits['ProcessDefinedStep'].to_numpy()).value_counts(normalize=True))
    # def print_hits_by_process(hits, processes):
    #     for process in processes:
    #         print(hits[hits['ProcessDefinedStep'] == process][['EventID', 'TotalEnergyDeposit', 'ProcessDefinedStep']])
    # processes = ['hIoni', 'Transportation', 'hadElastic', 'CoulombScat', 'none']
    # print_hits_by_process(hits, processes)

    # Histogram only
    # singles = uproot.open(singles_path)['Singles'].arrays(library='pd')
    # plt.hist(singles['TotalEnergyDeposit'], bins=100, range=(0, thickness)) # x-axis in MeV
    # plt.show()

    # Histogram + Landau fit
    import ROOT
    # gROOT.SetBatch(True) # comment to plot histogram and fit in pop-up canvas
    singles_rootfile = ROOT.TFile.Open(singles_path,'READ')
    singles_tree = singles_rootfile.Get('Singles')
    h = ROOT.TH1F('h', 'h', 1000, 0, source.energy.mono)
    singles_tree.Draw('TotalEnergyDeposit>>+h')
    r = h.Fit('landau', option='SQ') # xmax in MeV, 'Q' for quiet
    # print(round(r.Parameter(1),2),'MeV')