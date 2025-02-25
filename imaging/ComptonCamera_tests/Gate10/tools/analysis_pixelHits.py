# Utility functions to analyse output files
# Can be used in the main simulation script after sim.run() or offline (i.e. reading root files without simulation)
# Calling E1 the energy deposited in the Compton scattering, as in CCMod paper
import os
import sys
import numpy as np
import pandas
import uproot
import SimpleITK as sitk
import matplotlib.pyplot as plt
import cupy as cp
from pandas import Series
import imaging.ComptonCamera_tests.Gate10.tools.analysis_basics as analysis_basics
from imaging.ComptonCamera_tests.Gate10.tools.utils import *
from imaging.ComptonCamera_tests.Gate10.tools.utils import print_hits_inG4format

pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 1000)
pandas.set_option('display.float_format', lambda x: f'{x:.9}')  # G4 steps are logged with f'{x:.3}'

pixelHits_columns = ['PixelID', 'ToA', 'Energy']

def singles2pixelHits(file_path, nentries=None):
    if not os.path.isfile(file_path):
        sys.exit(f"File {file_path} does not exist, probably no hit produced...")
    else:
        print(f"Converting {file_path} to pixel hits")

    singles = uproot.open(file_path)['Singles'].arrays(library='pd', entry_stop=nentries)
    singles['HitUniqueVolumeID'] = singles['HitUniqueVolumeID'].astype(str).str.replace(r'0_', '', regex=True)
    singles.rename(columns={'HitUniqueVolumeID': 'PixelID'}, inplace=True)
    singles.rename(columns={'KineticEnergy': 'Energy'}, inplace=True)
    singles.rename(columns={'GlobalTime': 'ToA'}, inplace=True)

    return singles[pixelHits_columns]

def plot_pixelHits_byEventID(pixelHits, eventID, n_pixels, output_dir='output/'):
    event = pixelHits[pixelHits['EventID'] == eventID]
    if len(event) == 0:
        print(f"No pixel hit for event {eventID}")
        return
    print(f"Plotting pixel hits for event {eventID}")
    fig, ax = plt.subplots()
    h = ax.hist2d(event['PixelID'] % n_pixels, event['PixelID'] // n_pixels, bins=[n_pixels, n_pixels],
                  weights=event['Energy'], cmap='viridis', range=[[0, n_pixels], [0, n_pixels]])
    fig.colorbar(h[3], ax=ax, label='Pixel Charge')
    ax.set_aspect('equal')
    ax.set_xlabel('Pixel x')
    ax.set_ylabel('Pixel y')
    ax.set_title(f"Pixel hits for event {eventID}")
    plt.show()
    # plt.savefig(output_dir + f'pixelHits_event{eventID}.png')
    # plt.close()


def save_pixelHits_burdaman_format(pixelHits_df, output_path):
    # TODO set types correctly (else visu with TrackLab will not work)
    # TODO => https://software.utef.cvut.cz/tracklab/manual/a01627.html
    # TODO: set dummy values
    # insert a column with 0s at the 3rd position
    pixelHits_df.insert(2, 'fTOA', 0)
    print(pixelHits_df)
    pixelHits_df.to_csv(output_path, header=False, index=False, sep='\t')

    # Dummy header
    # TODO replace values with NaNs
    custom_header = """# Start of measurement: 10/1/2017 17:34:41.8467094
# Start of measurement - unix time: 1506872081.846
# Chip ID: H3-W00036
# Readout IP address: 192.168.1.105
# Back-end location: Satigny, CH
# Detector mode: ToA & ToT
# Readout mode: Data-Driven Mode
# Bias voltage: 229.72V
# THL = 1570 (0.875V)
# Sensor temperature: 58.9°C
# Readout temperature: 42.9°C
# ------- Internal DAC values ---------------
# Ibias_Preamp_ON:\t128\t(1.208V)
# Ibias_Preamp_OFF:\t8\t(1.350V)
# VPreamp_NCAS:\t\t128\t(0.702V)
# Ikrum:\t\t15\t(1.128V)
# Vfbk:\t\t164\t(0.891V)
# Vthreshold_fine:\t505\t(0.877V)
# Vthreshold_coarse:\t7\t(0.875V)
# Ibias_DiscS1_ON:\t100\t(1.109V)
# Ibias_DiscS1_OFF:\t8\t(1.321V)
# Ibias_DiscS2_ON:\t128\t(0.396V)
# Ibias_DiscS2_OFF:\t8\t(0.256V)
# Ibias_PixelDAC:\t128\t(0.984V)
# Ibias_TPbufferIn:\t128\t(1.169V)
# Ibias_TPbufferOut:\t128\t(1.077V)
# VTP_coarse:\t\t128\t(0.693V)
# VTP_fine:\t\t256\t(0.724V)
# Ibias_CP_PLL:\t\t128\t(0.557V)
# PLL_Vcntrl:\t\t128\t(0.874V)
# BandGap output:\t--- \t(0.684V)
# BandGap_Temp:\t\t--- \t(0.733V)
# Ibias_dac:\t\t--- \t(1.241V)
# Ibias_dac_cas:\t\t--- \t(1.004V)
# DACs: \t128\t8\t128\t15\t164\t505\t7\t100\t8\t128\t8\t128\t128\t128\t128\t256\t128\t128
# DACs Scans: \t1.208V\t1.350V\t0.702V\t1.128V\t0.891V\t0.877V\t0.875V\t1.109V\t1.321V\t0.396V\t0.256V\t0.984V\t1.169V\t1.077V\t0.693V\t0.724V\t0.557V\t0.874V\t0.684V\t0.733V\t1.241V\t1.004V
# -----------------------------------------------------------------------------------------------------------------------------
"""

    # Read the CSV file and add the custom header
    with open(output_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    lines.insert(0, custom_header)

    # Write the modified content back to the file
    with open(output_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)
