# Analysing hits
Geant4 steps can be logged in terminal with sim.g4_verbose, sim.g4_verbose_level_tracking = True, 1 (EventIDs are not logged, hence better do that with small number of events)
- ProcessDefinedStep (Gate) is pre-step, ProcName (G4) is post-step
  => thus when new track are generated in sensor, their ProcessDefinedStep is none.
- KineticEnergy (Gate) is pre-step, KinE (G4) is post-step
- StepLength (Gate) / StepLeng (G4) can be used to match hits (Gate) / steps (G4)


# QT issues with opengate 10.0.1
When using Qt-based code (e.g. napari) after simulation, the main.py script fails with:
```
WARNING: QObject::moveToThread: Current thread (0x57ad941535d0) is not the object's thread (0x57ad94c1ef50).
Cannot move to target thread (0x57ad941535d0)
WARNING: Could not load the Qt platform plugin "xcb" in "/home/billoud/PycharmProjects/GateContrib/venv/lib/python3.10/site-packages/opengate_core/plugins" even though it was found.
WARNING: This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.
Available platform plugins are: eglfs, linuxfb, minimal, minimalegl, offscreen, vnc, xcb, webgl.
```
Solution:
```
mv /home/billoud/PycharmProjects/GateContrib/venv/lib/python3.10/site-packages/opengate_core/plugins /home/billoud/PycharmProjects/GateContrib/venv/lib/python3.10/site-packages/opengate_core/plugins.bak`
```


# To simulate singles and timepix frame
# SINGLES
sc = sim.add_actor("DigitizerAdderActor", "Singles")
sc.input_digi_collection = "Hits"
sc.policy = "EnergyWeightedCentroidPosition"
sc.output_filename = 'CC_Singles.root'  # if hc.output_filename, there will be two branches in the file
# TIMEPIX FRAME
proj = sim.add_actor("DigitizerProjectionActor", "Projection")
proj.input_digi_collections = ["Singles"]
proj.spacing = [pitch, pitch]  # Set pixel spacing in mm
proj.size = [npix, npix]  # Image size in pixels (128x128)
proj.output_filename = 'projection.mhd'
