## Project Timeline Segmentation using Different Segmentation Models

This folder contains implementation of the different ways to segment a project timeline into bursts of activity. As discussed in the paper there are 4 different ways to segment a timeline:
1. __Kleinberg Segmentation__ - an infinite state automata on the frequency of occurance of an event
2. __Maximal Sum Burst Score Segmentation__ - segmentation of the timeline based on the intervals that maximize the burst score calculated at each timepoint.
3. __Hidden Markov Model Segmentation__ - segmentation based on the HMM states associated with high activity, trained on activity traces of the project.
4. __Text Tiling Segmentation__ - Segmenting the project timeline by looking at developer conversations using the TextTiling method

These segments are compared with each other by computing Beeferman's P_k. Each Folder contains the appropriate implementation. Please refer to the individual instructions for each of the method.
