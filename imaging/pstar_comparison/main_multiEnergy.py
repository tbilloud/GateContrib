# Script to analyse energy deposits of protons in silicon, to compare with pstar values:
# https://physics.nist.gov/PhysRefData/Star/Text/PSTAR.html
from time import sleep

import matplotlib.pyplot as plt
from networkx.algorithms.bipartite.basic import density
from opengate.geometry.materials import MaterialBuilder, dump_material_like_Gate
# -> ROOT must be installed and activated by running 'source /path/thisroot.sh'
# -> Run script from terminal: python -i main.py

from opengate.utility import g4_units, g4_best_unit
from opengate.managers import Simulation
import opengate_core
import ROOT
from ROOT import gPad, gROOT
import numpy as np

if __name__ == "__main__":
    sim, sim.output_dir = Simulation(), "output"
    um, mm, MeV = g4_units.um, g4_units.mm, g4_units.MeV
    sim.volume_manager.add_material_database('GateMaterials.db')
    sim.visu = False
    thickness = 10000 * um
    sim.world.material, sim.world.size = "Vacuum", [thickness * 1.01] * 2 + [thickness * 2.01]
    sensor = sim.add_volume("Box", "sensor")
    sensor.material, sensor.size, sensor.translation = "Silicon", [thickness] * 3, [0, 0, thickness / 2]
    hits = sim.add_actor('DigitizerHitsCollectionActor', 'Hits')
    hits.attached_to, hits.attributes = sensor.name, opengate_core.GateDigiAttributeManager.GetInstance().GetAvailableDigiAttributeNames()
    singles = sim.add_actor("DigitizerAdderActor", "Singles")
    singles.input_digi_collection, singles.policy = "Hits", "EnergyWeightedCentroidPosition"
    sim.random_engine, sim.random_seed = "MersenneTwister", 1
    source = sim.add_source("GenericSource", "source")
    source.particle, source.direction.type, source.direction.momentum = "proton", "momentum", [0, 0, 1]
    sim.physics_manager.physics_list_name = 'FTFP_BERT_EMZ' # 'G4EmStandardPhysics_option4'
    sim.physics_manager.global_production_cuts.all = 1e99 * mm
    step_size = 10 * um
    sensor.set_max_step_size(step_size)
    sim.physics_manager.set_user_limits_particles(['electron', 'positron', 'proton'])

    source.n = 1000
    pstar_MeVcm2_g = {'Silicon': {10: 34.59, 100: 5.838, 1000: 1.801}}
    density_g_cm3 = sim.volume_manager.material_database.FindOrBuildMaterial(
        sensor.material).GetDensity() / g4_units.g_cm3
    pstar_MeV_cm = {k: v * density_g_cm3 for k, v in pstar_MeVcm2_g[sensor.material].items()}
    pstar_MeV = {k: v * (thickness * 0.1) for k, v in pstar_MeV_cm.items()}  # thickness variable is in mm

    edep_MeV, histos = [], []
    c = ROOT.TCanvas('c1', 'c1', 1000, 800)
    c.Divide(2, 2)
    energies_MeV_list = list(pstar_MeV_cm.keys())
    for idx, energy in enumerate(energies_MeV_list):
        source.energy.mono = energy * MeV
        singles.output_filename = f'singles_{energy}.root'
        sim.run(start_new_process=True)
        singles_rootfile = ROOT.TFile.Open(f'{sim.output_dir}/singles_{energy}.root', 'READ')
        singles_tree = singles_rootfile.Get('Singles')
        c.cd(idx + 1)
        histos.append(ROOT.TH1F(f'h_{energy}', f'{energy} MeV protons', 10000, 0, 100))
        histos[idx].GetXaxis().SetTitle(f'energy deposited in {thickness}mm sensor [MeV]')
        singles_tree.Draw(f'TotalEnergyDeposit>>+h_{energy}')
        mean = histos[idx].GetMean()
        histos[idx].GetXaxis().SetRangeUser(mean * 0.2, mean * 1.8)
        r = histos[idx].Fit('landau', option='S', xmin=mean * 0.1, xmax=mean * 2)
        ROOT.gPad.Update()
        histos[idx].SetDirectory(ROOT.gROOT)
        edep_MeV.append(r.Parameter(1))

    c.cd(4)
    energies = np.array(energies_MeV_list, dtype=float)
    pstar_keV = 1000 * np.array(list(pstar_MeV.values()), dtype=float)
    g4_keV = 1000 * np.array(edep_MeV, dtype=float)
    gr_pstar = ROOT.TGraph(energies.shape[0], energies, pstar_keV)
    gr_pstar.SetMarkerStyle(21), gr_pstar.SetMarkerColor(4)
    gr_pstar.GetXaxis().SetTitle('Energy [MeV]')
    gr_pstar.GetYaxis().SetTitle('Deposited energy [keV]')
    gr_g4 = ROOT.TGraph(energies.shape[0], energies, g4_keV)
    gr_g4.SetMarkerStyle(21), gr_g4.SetMarkerColor(2)
    legend = ROOT.TLegend(0.2, 0.7, 0.48, 0.8)
    legend.AddEntry(gr_pstar, 'PSTAR', 'p')
    legend.AddEntry(gr_g4, 'Geant4', 'p')
    gr_pstar.Draw('AP'), gr_g4.Draw('SAME:P'), legend.Draw()
    gPad.SetLogx(), gPad.SetLogy(), gr_pstar.GetYaxis().SetRangeUser(10, 1e5), gPad.Update()
    print(f'geant4/pstar ratios for energies {energies} MeV:',np.round(100 * g4_keV / pstar_keV))
    c.SaveAs(f'thickness{int(thickness / um)}um_step{int(step_size / um)}um_{sim.physics_manager.physics_list_name}.png')
