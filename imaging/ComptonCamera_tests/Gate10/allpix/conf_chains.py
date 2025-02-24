# Different simulation (sub-)chains for Allpix
# https://allpix-squared.docs.cern.ch/docs/03_getting_started/06_simulation_chain/

# QDC: charge-to-digital converter
# TDC: time-to-digital converter
# https://allpix-squared.docs.cern.ch/docs/08_modules/defaultdigitizer/

# For basic tests
# => input hits do not always produce output pixel hits
# TODO pixelID does not always match the pixelID in the output...
chain_simple = """
[GenericPropagation]
[SimpleTransfer]
max_depth_distance = 1m
[DefaultDigitizer]
threshold = 0e
"""

chain_advanced = """
[ElectricFieldReader]
model = "constant"
bias_voltage = -1000V
[GenericPropagation]
mobility_model = "constant"
mobility_electron = 10000cm*cm/V/s
mobility_hole = 500cm*cm/V/s
[PulseTransfer]
[DefaultDigitizer]
threshold = 1e
threshold_smearing = 0
qdc_resolution = 8 # Resolution of the QDC in units of bits. Thus, a value of 8 would translate to a QDC range of 0 to 255. A value of 0bit switches off the QDC simulation and returns the actual charge in electrons. Defaults to 0.
qdc_smearing = 0 # Standard deviation of the Gaussian noise in the ADC conversion (after applying the threshold). Defaults to 300 electrons.
qdc_slope = 10e # Slope of the QDC calibration in electrons per ADC unit (unit: e). Defaults to 10e.
qdc_offset = -1 # Offset of the QDC calibration in electrons. In order to simulate a ToT (time-over-threshold) device, this offset should be configured to the negative value of the threshold. Defaults to 0.
tdc_resolution = 0 # Resolution of the TDC in units of bits. Thus, a value of 8 would translate to a TDC range of 0 to 255. A value of 0bit switches off the TDC simulation and returns the actual time of arrival in nanoseconds. Defaults to 0.
tdc_smearing = 0
tdc_slope = 0 # Slope of the TDC calibration in nanoseconds per TDC unit (unit: ns). Defaults to 10ns.
tdc_offset = 0 # Offset of the TDC calibration in nanoseconds. Defaults to 0.
"""

# TODO
chain_advanced_csa = """
[TransientPropagation]
[PulseTransfer]
[CSADigitizer]
"""
