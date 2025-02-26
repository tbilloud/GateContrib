# Functions to process pixelHits dataframes

import os
import sys
import pandas
import pandas as pd
import uproot
import matplotlib.pyplot as plt
from imaging.ComptonCamera_tests.Gate10.tools.utils import *
import matplotlib.colors as mcolors
from matplotlib.ticker import MaxNLocator

from imaging.ComptonCamera_tests.Gate10.tools.utils import get_pixID

pandas.set_option('display.max_columns', 100)
pandas.set_option('display.width', 400)
pandas.set_option('display.max_rows', 1000)
pandas.set_option('display.float_format', lambda x: f'{x:.9}')  # G4 steps x:.3

PIXEL_ID = 'PixelID_int16'
TOA = 'ToA_ns'
ENERGY = 'Energy_keV'
pixelHits_columns = [PIXEL_ID, TOA, ENERGY]
EVENTID = 'EventID'
TOT = 'ToT'
POSITION_X = 'PositionX'
POSITION_Y = 'PositionY'
POSITION_Z = 'PositionZ'
simulation_columns = [EVENTID, TOT, POSITION_X, POSITION_Y, POSITION_Z]


def singles2pixelHits(file_path):
    if not os.path.isfile(file_path):
        sys.exit(f"{file_path} does not exist, probably no hit produced...")
    else:
        print(f"Converting {file_path} to pixel hits")

    singles = uproot.open(file_path)['Singles'].arrays(library='pd')
    singles['HitUniqueVolumeID'] = singles['HitUniqueVolumeID'].astype(
        str).str.replace(r'0_', '', regex=True)
    singles.rename(columns={'HitUniqueVolumeID': PIXEL_ID}, inplace=True)
    singles[PIXEL_ID] = singles[PIXEL_ID].astype(int)
    singles.rename(columns={'TotalEnergyDeposit': ENERGY}, inplace=True)
    singles[ENERGY] = singles[ENERGY] * 1e3  # Convert MeV to keV
    singles.rename(columns={'GlobalTime': TOA}, inplace=True)
    return singles[pixelHits_columns]


def plot_pixelHits(pixelHits_df, n_pixels, log_scale=[False, False]):
    df, np = pixelHits_df, n_pixels
    x, y = zip(*df[PIXEL_ID].apply(get_pixID_2D, args=(np,)))

    fig, ax = plt.subplots(1, 2, figsize=(12, 6))

    nc, ne = [mcolors.LogNorm() if log else None for log in log_scale]

    hc = ax[0].hist2d(x, y, bins=[np] * 2, range=[[0, n_pixels]] * 2, norm=nc)
    cb = fig.colorbar(hc[3], ax=ax[0], label='Count')
    cb.locator = MaxNLocator(integer=True)
    cb.update_ticks()
    ax[0].set_title('Hit Count')

    he = ax[1].hist2d(x, y, bins=[np] * 2, weights=df[ENERGY], range=[[0, np]] * 2, norm=ne)
    fig.colorbar(he[3], ax=ax[1], label='Energy Sum')
    ax[1].set_title('Energy Sum')

    for a in ax:
        a.set_aspect('equal')
        a.set_xlabel('Pixel x')
        a.set_ylabel('Pixel y')

    plt.tight_layout()
    plt.show()


def pixelHits2burdaman(pixelHits_df, out_path):
    # TODO set types correctly (else visu with TrackLab will not work)
    # TODO => https://software.utef.cvut.cz/tracklab/manual/a01627.html
    # TODO: set dummy values
    # insert a column with 0s at the 3rd position
    pixelHits_df.insert(2, 'fTOA', 0)
    print(pixelHits_df)
    pixelHits_df.to_csv(out_path, header=False, index=False, sep='\t')

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
    with open(out_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    lines.insert(0, custom_header)

    # Write the modified content back to the file
    with open(out_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)


def allpixTxt2pixelHit(text_file, n_pixels=256):
    # TODO adapt to different simulation chains

    df = pd.DataFrame(columns=pixelHits_columns + simulation_columns)
    rows = []

    with open(text_file, "r") as file:
        event_id = None
        for line in file:
            line = line.strip()

            if line.startswith("==="):
                event_id = int(
                    line.split()[1]) - 1  # allpix adds 1 to event ID
                continue

            if line.startswith("---"):
                continue

            if line.startswith("PixelHit"):
                parts = line.split()
                x, y = int(parts[1].strip(',')), int(parts[2].strip(','))
                pixel_id = get_pixID(x, y, n_pixels=n_pixels)
                tot = float(parts[3].strip(','))
                toa = float(parts[4].strip(','))
                global_time = float(parts[5].strip(','))
                position_x = float(parts[6].strip(','))
                position_y = float(parts[7].strip(','))
                position_z = float(parts[8].strip(','))

                rows.append({
                    EVENTID: event_id,
                    PIXEL_ID: pixel_id,
                    TOT: tot,
                    ENERGY: tot,  # TODO: temporary
                    TOA: global_time + toa,
                    # because ToA is measured from the beginning of the event
                    POSITION_X: position_x,
                    POSITION_Y: position_y,
                    POSITION_Z: position_z
                })

    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
    return df