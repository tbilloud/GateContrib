## Description
This example is an attempt to reproduce the simulations of the compton camera module's publication:

https://doi.org/10.1088/1361-6560/ab6529

It was done using Gate v9.2, which was based on the old digitizer implementation. Starting from Gate v9.3, a new 
digitization was adopted and the commands in this script are no longer valid.

The example also shows how to use the offline processing tools, which allow to perform digitization on .root files without the 
need of a full simulation: 

https://opengate.readthedocs.io/en/latest/compton_camera_imaging_simulations.html#offline-processing
 
## Set-up
The camera consists of two scintillator crystals (geometry.mac). There are two sets of simulation in the paper: one with
and one without the structure of the camera. This example only include the latter, i.e. two sensitive volumes alone.
  
## CCMod actor:
See the original example (ComptonCamera_TODO_GND) for a detailed description of the CCMod actor.

## Output
Three .root output files are created, one for hits, one for singles and another one for sequence coincidences.
There is a folder with output files. 

## Tools: Analysis (python script)
Python scripts are provided to reproduce some figures of the paper.




