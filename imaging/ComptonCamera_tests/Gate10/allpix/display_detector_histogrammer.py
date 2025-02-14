# script to plot output in module Detector Histogrammer
import uproot
from matplotlib import pyplot as plt
import mplhep

file_path = "../output/modules.root"
detector_name = "0_0"

f = uproot.open(file_path)
histo_path = "DetectorHistogrammer/0_0/"

print(f.keys())
print(f[histo_path+"hit_map"].to_hist())

# mplhep.hist2dplot(f[histo_path+"hit_map"].to_hist())
# plt.show()

# mplhep.hist2dplot(f[histo_path+"hit_map_global"].to_hist())
# plt.show()
#
# mplhep.hist2dplot(f[histo_path+"hit_map_local"].to_hist())
# plt.show()
#
# mplhep.hist2dplot(f[histo_path+"hit_map_local_mc"].to_hist())
# plt.show()
#
mplhep.hist2dplot(f[histo_path+"charge/charge_map"].to_hist())
plt.show()