'''
Fano factor summary for paper
'''

import os
import sys
import csv
import pandas as pd
import cPickle as pickle
from collections import defaultdict
import numpy as np
import argparse
import statistics

parser = argparse.ArgumentParser()
#parser.add_argument('--valid_projects', help='Path for the list of projects we\`re considering for this metric',
                #default='Sample_Data/congruence/burst_issue_inventory.txt')
parser.add_argument('--input_file', help='Path for the input pickle containing fano factor per project', 
                default='Sample_Data/HMM/results/fano_factor_per_project.pickle')

args, unknown = parser.parse_known_args()

factors = pickle.load(open(args.input_file,"rb"))
#valid = [p.strip() for p in open(args.valid_projects)]
valid = factors.keys()


values = [factors[f] for f in factors if f in valid]

print "Average value of the Fano Factor for projects = " + str(statistics.mean(values))
print "Median value of the Fano Factor for projects = " + str(statistics.median(values))
print "Percentage of projects with Fano Factor > 1 = " + str((len([v for v in values if v > 1.0])*100.0)/len(values))
