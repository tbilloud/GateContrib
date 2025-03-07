# Simulating a single layer Compton camera

- Use Gate10 to simulate a single layer Compton camera.
- Optionally add Allpix2 to simulate detector a semiconductor pixel detector response (e.g. Timepix3).
- Reconstruct cones from:
  - Geant4 'hits'
  - Gate 'singles'
  - Allpix2 'pixel hits' (WIP)
  - measured data
- Validate simulation/measurement of gamma point sources
- Reconstruct 3D image with basic backprojection
- WIP: reconstruct 3D image with advanced algorithms (e.g. CoReSi)

Requires:
- git
- python3
- 10 GB of disk space

Tested with:
- Ubuntu 22.04 and 24.04
- python 3.10
- Gate 10.0.1  

## Installation

### 1) Get the code
```
git clone https://github.com/tbilloud/GateContrib
cd GateContrib
git checkout compton-camera-tests
cd imaging/ComptonCamera_tests/Gate10
```

### 2) Create a virtual environment
```
python -m venv opengate_env
source opengate_env/bin/activate
pip install --upgrade pip
```

### 3) Install Gate10
https://opengate-python.readthedocs.io/en/master/user_guide/user_guide_installation.html#
```
pip install opengate
opengate_tests
```
This downloads Geant4 datasets, which takes a while.

### 4) Optional: Install Allpix2
https://allpix-squared.docs.cern.ch/docs/02_installation/  
Install ROOT 6:  
https://root.cern/install/  
Then install Allpix2 without Geant4:  
```
git clone https://gitlab.cern.ch/allpix-squared/allpix-squared
cd allpix-squared
mkdir build
cd build
cmake -DCMAKE_INSTALL_PREFIX=../install-noG4 -DBUILD_GeometryBuilderGeant4=OFF -DBUILD_DepositionCosmics=OFF -DBUILD_DepositionGeant4=OFF -DBUILD_DepositionGenerator=OFF -DBUILD_GDMLOutputWriter=OFF -DBUILD_VisualizationGeant4=OFF ..`
make -j4
make install
```
### 3) Install the required python packages
`pip install -r requirements.txt`

### 4) Set environment:
`export PYTHONPATH=/path/to/your/project:$PYTHONPATH`

## Getting started
Run a basic test:
`python3 main.py`

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
