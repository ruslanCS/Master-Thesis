# Master-Thesis
These are scripts that I have developed throughout my master thesis about optimal feedback control in human reaching movements. These scripts were used to analyze time-series movement data. The data were used to train a model that predicts human reaching movements based optimal control theory.

IndividualAnalysis.ipynb extracts the relevant reaching movements from a continuous stream of full body movements collected from subjects performing a reaching experiment in VR and recorded using a PhaseSpace motion capture system. This script was used to calculate typical movement parameters and to obtain mean trajectories by applying dynamic time warping (DTW) and linear interpolation. 

GroupAnalysis.ipynb uses the results obtained through the analyses of each individual subjects to calculate corresponding results on a group level and plots them. 

CompareConditions.ipynb compares mean trajectories and other relevant movement parameters between 13 different experimental conditions. 
