'''
Extract a burst as contiguous day intervals. 
Currently considering 3 days as the valid interval to be considered in the microburst.
A day beyond a 3 days from the last seen activity is considered to be forming a new burst of activity.
'''

import os
import sys
import pandas as pd
import cPickle as pickle
from datetime import datetime
from dateutil import relativedelta
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--filtered_dir', help='Directory with filtered states', default='Sample_Data/HMM/results/filtered_states/')
parser.add_argument('--output_file', help='Output filename for the pickled dictionary {project:[bursts]}', default='Sample_Data/HMM/results/daily_bursts.pickle')
args, unknown = parser.parse_known_args()

filtered_dir = args.filtered_dir
output_file = args.output_file
final_dict = {}

for filename in os.listdir(filtered_dir):
	if '.csv' not in filename:
		continue
	project_name = filename.split('_with_state_filtered.csv')[0]
	print "Processing for the project = ", project_name
	project_data = pd.read_csv(os.path.join(filtered_dir, filename))
	dates = list(project_data['period'])
	dates = [x for x in dates if str(x) != 'NullState']
	dates = sorted(dates)
	dates = list(map(lambda x: str(x), dates))
	dates = list(map(lambda x: x[0:4] + "/" + x[4:6] + "/" + x[6:8], dates))
	dates = list(map(lambda x: datetime.strptime(x, '%Y/%m/%d'), dates))
	final_dict[project_name] = []
	cur_burst = ""
	insertion = False
	day_delta = 0
	for i in range(len(dates)-1):
		cur_date = dates[i]
		next_date = dates[i+1]
		if len(cur_burst) == 0:
			insertion = False
			cur = cur_date.strftime("%Y/%m/%d")
			cur_burst = cur + "-"
		day_delta = next_date - cur_date
		day_delta = abs(day_delta.days)
		if day_delta > 3:
			if i+1 < len(dates)-1:
				insertion = True
			cur = cur_date.strftime("%Y/%m/%d")
			cur_burst += cur
			final_dict[project_name].append(cur_burst)
			cur_burst = ""          
	if insertion == False:
		if len(dates) == 1:
			cur_date = dates[0]
			cur = cur_date.strftime("%Y/%m/%d")
			final_dict[project_name].append(cur + "-" + cur)
		elif day_delta > 3:
			nxt = next_date.strftime("%Y/%m/%d")
			final_dict[project_name].append(nxt + "-" + nxt)
		else:
			nxt = next_date.strftime("%Y/%m/%d")
			cur_burst += nxt
			final_dict[project_name].append(cur_burst)

with open(output_file, 'wb') as p_pickle:
	pickle.dump(final_dict, p_pickle)




