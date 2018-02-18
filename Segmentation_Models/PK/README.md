# Beeferman's Pk

This folder contains an implementation of the segmentation model evaluation metric from: _Beeferman, Doug, Adam Berger, and John Lafferty. "Statistical models for text segmentation."_

## Dependencies
1. __Pandas__ - https://pandas.pydata.org/

## Data
Following are the inputs needed:
1. __Project Daily Activity Pickle__ - Calculated as a helper pickle while computing TT segments (refer Segmentation_Models/TT_Segments/)
2. __Project Burst Pickles__ - All the segmentation boundaries predicted by each of the segmentation models pickled in a consistent format. (Outputs from each of the segmentation models)

## Execution Steps
There are two scrips in the implementation of this measure. One measures the pairwise P_k values for the non-lexical segmentation models while the other measures the P_k with the TT segments. Please have a look at the file for the commandline arguments and usage:

1. __Compute Pairwise Pk__ - Computes the average pairwise Pk values between each pair of HMM, Max-Sum and Kleinberg segmentation models
> Script : __pairwise_pk.py__

2. __Compute Pk with TT Segments__ - Computed pairwise Pk values between each of  HMM, Max-Sum and Kleinberg segmentation models with the segmentation outputs from the TextTiling model.
> Script: __compute_pk_tt.py__ 