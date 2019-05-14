'''
Puts Klein bursts in format [burst1, burst2,....]. The input is in the form of {intensity:[burst]} (Output of the R Script)
'''

import os
import sys
import cPickle as pickle
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--klein_pickle', help='Pickle file containing the klein bursts of the project in the {project:{intensity:[burst]}} format',
          default = "Sample_Data/alternate_bursts/klein/level_bursts.pickle")
parser.add_argument('--output_pickle', help='Output pickle for the formatted burst of the format {project:[burst]}',
          default = "Sample_Data/alternate_bursts/klein/final_bursts.pickle")
args, unknown = parser.parse_known_args()


klein_pickle = args.klein_pickle
output_pickle = args.output_pickle

klein_bursts = pickle.load(open(klein_pickle, 'rb'))
formatted = {}

for ix, project in enumerate(klein_bursts):
    print "Project ",ix,":", project
    bursts = []

    for intensity, burst_list in klein_bursts[project].items():
        for start,end in burst_list:
            start = start.replace('-', '/')
            end = end.replace('-', '/')
            burst = start + '-' + end
            bursts.append(burst)
        bursts = sorted(bursts)
    formatted[project] = bursts

with open(output_pickle, 'wb') as p_pickle:
    pickle.dump(formatted, p_pickle)
