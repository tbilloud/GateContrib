# Simulating a Timepix3 single layer Compton camera

Uses Gate10 and (optionally) Allpix2  
Requirements:
- python3
- Gate10
Validated with Ubuntu 22.04 / Gate 10.0.1  

## Installation
### 1) Install Gate10
```
python -m venv opengate_env
source opengate_env/bin/activate
pip install --upgrade pip
pip install opengate
```
### 2) Optional: Install Allpix2
...

### 3) Python packages
TODO

## Analysing hits
Geant4 steps can be logged in terminal with sim.g4_verbose, sim.g4_verbose_level_tracking = True, 1 (EventIDs are not logged, hence better do that with small number of events)
- ProcessDefinedStep (Gate) is pre-step, ProcName (G4) is post-step
  => thus when new track are generated in sensor, their ProcessDefinedStep is none.
- KineticEnergy (Gate) is pre-step, KinE (G4) is post-step
- StepLength (Gate) / StepLeng (G4) can be used to match hits (Gate) / steps (G4)


## QT issues with Gate 10.0.1
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

## Using the DigitizerProjectionActor
This actor could give an image with integrated sum of pixel hits over events. But using it gives:  
`Exception: Sorry, cannot (yet) use ProjectionActor with repeated volumes, set 'authorize_repeated_volumes' to False`  
When fixed, use plot_DigitizerProjectionActor(sim) from analysis_basics.py and:  
```
proj = sim.add_actor("DigitizerProjectionActor", "Projection")
proj.input_digi_collections = ["Singles"]
proj.authorize_repeated_volumes = True
proj.spacing = [pitch, pitch]
proj.size = [npix, npix]
proj.output_filename = 'projection.mhd'
```

## Allpix2

Allpix2 is a C++ software for precise simulation of pixel detectors.
It simulates the transport of charge carriers in semiconductor sensors and their signal induction.
It is used primarily for detector R&D in particle physics.  
https://cern.ch/allpix-squared


Allpix2 can read the hits root file from Gate.
Combined with Gate10, the entire simulation can be done with a single python file.
For this, Allpix2 should be installed without Geant4 modules:
`cmake -DCMAKE_INSTALL_PREFIX=../install-noG4 -DBUILD_GeometryBuilderGeant4=OFF -DBUILD_DepositionCosmics=OFF -DBUILD_DepositionGeant4=OFF -DBUILD_DepositionGenerator=OFF -DBUILD_GDMLOutputWriter=OFF -DBUILD_VisualizationGeant4=OFF ..`

Running main.py does the following:
1) run Gate10 and creates the hits root file
2) generate the three .conf files needed for Allpix2
3) run Allpix2 and creates the output files data.root and modules.root

In the `tools` folder, there are scripts to plot/analyse the results.
See Allpix2 documentation for more details on the configuration files and output files.
