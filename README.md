# Python-PAR-REC-Reader-
Python class dedicated to reading and processing PAR REC files from Philips MRI Scanners

## General Informations
This class aims to facilitate handling of PAR and REC files, using Python. 
Code has been developed based on previous Matlab formulation : https://www.mathworks.com/matlabcentral/fileexchange/38797-matlab-par-rec-reader-readparrec42-m

## Inputs:
Class instantiation requires paths of PAR and REC files
- PAR file is a text file containing general informations about the acquisition and more specific image related parameters.
- REC file contains images. Images are built based on extracted PAR informations.

### Comments:
This code has been written in order to be as flexible as possible. However, due to initial PAR file structure, some adjustements my be required regarding sequences or updates.  Comments in the code are dedicated to help.
