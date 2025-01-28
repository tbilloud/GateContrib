# Simulate the response of semiconductor pixel detectors using Gate10 and Allpix2

Allpix2 is a C++ software for precise simulation of pixel detectors.
It simulates the transport of charge carriers in semiconductor sensors and their signal induction.
It is used primarily for detector R&D and is hosted by CERN.
Documentation: https://cern.ch/allpix-squared

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
