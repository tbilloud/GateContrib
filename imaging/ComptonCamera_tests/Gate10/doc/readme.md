## Analysing Gate hits
Geant4 steps can be logged in terminal with sim.g4_verbose, sim.g4_verbose_level_tracking = True, 1 (EventIDs are not logged, hence better do that with small number of events)
- ProcessDefinedStep (Gate) is pre-step, ProcName (G4) is post-step
  => thus when new track are generated in sensor, their ProcessDefinedStep is none.
- KineticEnergy (Gate) is pre-step, KinE (G4) is post-step
- StepLength (Gate) / StepLeng (G4) can be used to match hits (Gate) / steps (G4)

## Clustering hits
When using Allpix2, the output is in pixel hits, as when measuring with a Timepix3 detector. Those are different from gate hits (gHits).
To reconstruct photon interactions in Timepix3 sensor from pixel hits, i.e. their 3D position, time and energy, different algorithms can be used.

### Energy
Timepix3 measures the energy deposited in individual pixels via TOT (Time-Over-Threshold).
When a detector is calibrated with a per-pixel energy calibration procedure, TOT can be converted to energy.

### Time (TOA)
Time-of-Arrival (TOA) is measured with Timepix3 with 1.6 ns granularity.

A so-called time-walk correction can be applied to improve precision, since higher energy deposits induce faster pulses on pixel pre-amplifiers. Precision???

Even though Compton, photo-electric and fluorescent events occur almost simultaneously (within few ps?), the time it takes for the charge carriers to drift to the pixel electrode can be long (depending on semiconductor and bias voltage) and it depends on the depth of interaction.

Drift time = distance / drift speed = distance / (mobility * electric field) 
Drift time = (distance * thickness) / (mobility * voltage)

Mobility in Silicon (wikipedia):
- electrons: ~1000 cm^2/Vs
- holes: ~450 cm^2/Vs

Mobility in CdTe (wikipedia):
- electrons: ~1100 cm^2/Vs
- holes: ~100 cm^2/Vs

Examples of drift time over full sensor thickness:
1mm CdTe @ 1000V:
  e-: 10 ns
  holes: 100 ns

