# Simulate a single layer Compton camera

- Use Gate10 to simulate a single layer Compton camera.
- Optionally add Allpix2 to simulate detector a semiconductor pixel detector response (e.g. Timepix3).
- Reconstruct cones from:
  - Geant4 'hits'
  - Gate 'singles'
  - Allpix2 'pixel hits' (WIP)
  - measured data (WIP)
- Validate simulation/measurement of gamma point sources
- Reconstruct 3D image with basic backprojection
- WIP: reconstruct 3D image with advanced algorithms (e.g. CoReSi)

Requires:
- python3
- 20 GB of disk space
- Optional: Allpix2, ROOT 6, CUDA

Tested with:
- Ubuntu 22.04 and 24.04
- python 3.10
- Gate 10.0.1  

## Installation

### 1) Download or clone and checkout branch compton-camera-tests: 
```
git clone -b compton-camera-tests https://github.com/tbilloud/GateContrib
```

### 2) Create a virtual environment
```
cd GateContrib/imaging/ComptonCamera_tests/Gate10
python3 -m venv venv
source venv/bin/activate
```

### 3) Install required python packages
`pip install -r requirements.txt`  
To use the GPU-based functions (point source validation, reconstruction), install CUDA and the Cupy package suited to your CUDA version, e.g.  
`pip install cupy-cuda115`

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


### 5) Set environment:
```
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=2000000
```

## Getting started
Run the test:  
`python3 main.py`  
The 1st time you run a simulation, Gate10 will install Geant4 datasets, which can take a while. This is done only once.


### QT issues with Gate 10.0.1
When using Qt-based code (e.g. napari) after simulation, the main.py script might fail with:
```
WARNING: QObject::moveToThread: Current thread (0x57ad941535d0) is not the object's thread (0x57ad94c1ef50).
Cannot move to target thread (0x57ad941535d0)
...
```

Solution:
```
mv /path-to-virtual-environment/lib/python3.10/site-packages/opengate_core/plugins /path-to-virtual-environment/lib/python3.10/site-packages/opengate_core/plugins.bak`
```

### Allpix2

Allpix2 is a C++ software for precise simulation of pixel detectors.
It simulates the transport of charge carriers in semiconductor sensors and their signal induction.
It is used primarily for detector R&D in particle physics.  
https://cern.ch/allpix-squared


Allpix2 can read the hits root file from Gate.
Combined with Gate10, the entire simulation can be done with a single python file, using the function
gHits2allpix2pixelHits() after the sim.run() in the main.py script. It does the following:
1) run Gate10 and creates the hits root file
2) generate the three .conf files needed by Allpix2
3) run Allpix2 and creates the output files data.txt and modules.root in the sub-folder 'allpix'
4) read data.txt and return a pandas dataframe with the pixel hits