## Analysing Gate hits
Geant4 steps can be logged in terminal with sim.g4_verbose, sim.g4_verbose_level_tracking = True, 1 (EventIDs are not logged, hence better do that with small number of events)
- ProcessDefinedStep (Gate) is pre-step, ProcName (G4) is post-step
  => thus when new track are generated in sensor, their ProcessDefinedStep is none.
- KineticEnergy (Gate) is pre-step, KinE (G4) is post-step
- StepLength (Gate) / StepLeng (G4) can be used to match hits (Gate) / steps (G4)

## Clustering hits
To reconstruct photon interactions in Timepix3 sensor, i.e. their 3D position, time and energy, different algorithms can be used.

### Time (TOA)
Time-of-Arrival (TOA) is measured with Timepix3 with 1.6 ns granularity.

A so-called time-walk correction can be applied to improve precision, since higher energy deposits induce faster pulses on pixel pre-amplifiers. Precision???

Even though Compton, photo-electric and fluorescent events occur almost simultaneously (within few ps?), the time it takes for the charge carriers to drift to the pixel electrode can be long (depending on semiconductor and bias voltage) and it depends on the depth of interaction. This can be used to determine depths of interactions.

Drift time = distance / (mobility * electric field)

Mobility in Silicon (wikipedia):
- electrons: ~1000 cm^2/Vs
- holes: ~450 cm^2/Vs

Mobility in CdTe (wikipedia):
- electrons: ~1100 cm^2/Vs
- holes: ~100 cm^2/Vs

Drift time examples:
1mm in a CdTe sensor with 100V bias: 1 us for electrons, 10 us for holes