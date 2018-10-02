'''
Breaks up bursts into shorter bursts, in order to see how the model applies
to them.
'''

import os
import sys
import random
import csv
import glob
import calendar
import cPickle as pickle
import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta
import argparse


csv.field_size_limit(sys.maxsize)

parser = argparse.ArgumentParser()
parser.add_argument('--burst_pickle', help='Pickle file containing the project burst information', default='Sample_Data/HMM/results/daily_bursts.pickle')
parser.add_argument('--shortened_burst_pickle', help='Output pickle file containing artificially short bursts', default='Sample_Data/HMM/results/shortened_bursts.pickle')
parser.add_argument('--new_burst_length', help='Length of new shorter bursts, in days. If a full burst is not a multiple of this, there will be one short stub burst.  If a full burst is shorter than this, it will not be used', default='1')
parser.add_argument('--number_of_bursts', help='Number of new shorter bursts to generate', default='1000')
parser.add_argument('--shortest_burst_to_break', help='Do not break up bursts shorter than this (in days)', default='1')
args, unknown = parser.parse_known_args()


project_burst_pickle = args.burst_pickle
shortened_burst_pickle = args.shortened_burst_pickle
number_of_bursts = int(args.number_of_bursts)
shortest_burst_to_break = int(args.shortest_burst_to_break)
new_burst_length = int(args.new_burst_length)

burst_dict = pickle.load(open(project_burst_pickle, 'rb'))
projects = burst_dict.keys()

def parse_burst(burst):
    parts= burst.split('-')
    low = parts[0]
    high = parts[1]
    low = low.replace('/', '-')
    high_str = high.replace('/', '-')
    low = datetime.strptime(low, '%Y-%m-%d')
    high = datetime.strptime(high_str, '%Y-%m-%d') + timedelta(days=1)
    duration = (high - low).days
    return (low,high,duration)

print "Beginning with ", sum([len(burst_dict[p]) for p in burst_dict]), "bursts in ", len(burst_dict), " projects"
print "Eliminating bursts < " + args.shortest_burst_to_break + " from consideration"
new_bursts = []
new_projects = set()
for p in burst_dict.keys():
    for b in burst_dict[p]:
        parsed = parse_burst(b)
        if parsed[2] >= shortest_burst_to_break:
            new_bursts.append((p, parsed[0],parsed[1],parsed[2]))

print "Remaining: ", len(new_bursts), "bursts in ", len(new_projects), " projects"
random.shuffle(new_bursts)
final_bursts = []
while len(final_bursts) < number_of_bursts:
    tobreak = new_bursts.pop()
    for dt in [tobreak[1] + timedelta(days=k) for k in range(0,tobreak[3],new_burst_length)]:
        final_bursts.append((tobreak[0], dt, min(dt + timedelta(days=new_burst_length), tobreak[2]))) 

print "Broke into ", len(final_bursts), "bursts"
final = dict()
for f in final_bursts:
    if f[0] not in final: final[f[0]] = []
    final[f[0]].append(f[1].strftime("%Y/%m/%d") + "-" + (f[2] - timedelta(days=1)).strftime("%Y/%m/%d"))

pickle.dump(final, open(shortened_burst_pickle, "wb"))


