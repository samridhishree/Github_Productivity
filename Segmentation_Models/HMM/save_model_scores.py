'''
Computes the log probability under the given model for the train and the test data
'''

import os
import sys
import joblib
import csv
import h5py
import warnings
from hmmlearn import hmm
import argparse
import unicodedata

csv.field_size_limit(sys.maxsize)
warnings.filterwarnings('ignore')

parser = argparse.ArgumentParser()
parser.add_argument('--data_file', help='Compressed data used while training the HMM',\
    default='Sample_Data/HMM/hmm_data.hdf5')
parser.add_argument('--model_dir', help='Models saved by HMM',\
    default='Sample_Data/HMM/results/GaussianHMMdiag/')
parser.add_argument('--output_file', help='CSV file containeing the model scores',\
    default='Sample_Data/HMM/results/model_scores.csv')



args, unknown = parser.parse_known_args()
data_file = args.data_file
model_dir = args.model_dir
output_file = args.output_file

# Load the compressed data
d = h5py.File(data_file,'r')
final_train_seq = d['train/traindata'][:]
train_lengths = d['train/trainlengths'][:]
final_test_seq = d['test/testdata'][:]
test_lengths = d['test/testlengths'][:]

f = open(output_file,'w')
writer = csv.writer(f)
writer.writerow(['No. of States','Train Score','Test Score','Convergence'])

for model_file in os.listdir(model_dir):
    nstates = model_file.split("states")[0]
    # Load the model
    model = joblib.load(os.path.join(model_dir, model_file))
    print "Calculating the score"
    trainscore = model.score(final_train_seq, lengths=train_lengths)
    testscore = model.score(final_test_seq, lengths=test_lengths)
    #scoringtime = (time.time()-start_time)/60
    print "Scoring done"
    writer.writerow([nstates, trainscore, testscore, model.monitor_.iter])

f.close()
