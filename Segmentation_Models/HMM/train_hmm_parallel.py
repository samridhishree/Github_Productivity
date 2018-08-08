'''
Trains a Gaussian HMM using hmmlearn.
Iterates among a range of states where the best fit is found based on the likelihood.
Pickles and saves the file.
'''

import os
import csv
import sys
import time
import datetime
import h5py
import joblib
import warnings
from hmmlearn import hmm
from multiprocessing import Process
import argparse

warnings.filterwarnings('ignore')

parser = argparse.ArgumentParser()
parser.add_argument('--data_file', \
                    help='The compressed hdf5 train/dev/test data for HMM', \
                    default='Sample_Data/HMM/hmm_data.hdf5')
parser.add_argument('--output_dir', \
                    help='Directory to save the trained models and the model scores', \
                    default='Sample_Data/HMM/results/')
args, unknown = parser.parse_known_args()

data_file = args.data_file
output_dir = args.output_dir

try:
    os.makedirs(output_dir)
except:
    pass

# Define the target function to be called in parallel
def train_hmm(nstates, final_train_seq, train_lengths, final_test_seq, test_lengths):
    covartype="diag"
    modeltype="GaussianHMM"

    model=hmm.GaussianHMM(n_components=nstates, n_iter=500, covariance_type=covartype, verbose=True, tol=0.1)
    print "Training "+str(nstates)+" states"
    start_time = time.time()
    model = model.fit(final_train_seq,train_lengths)
    print "Fitting Done for " + str(nstates) + "states"
    fittingtime = (time.time()-start_time)/60
    start_time = time.time()
    print "Calculating the score for " + str(nstates) + "states"
    trainscore = model.score(final_train_seq, lengths=train_lengths)
    testscore = model.score(final_test_seq, lengths=test_lengths)
    scoringtime = (time.time()-start_time)/60
    print "Scoring done for " + str(nstates) + "states"
    dir_to_save = os.path.join(output_dir, modeltype + covartype)
    file_path = os.path.join(dir_to_save, str(nstates) + 'states') 
    try:
        os.makedirs(dir_to_save)
    except:
        pass
    joblib.dump(model,file_path)


# Load the compressed data
d = h5py.File(data_file,'r')
final_train_seq = d['train/traindata'][:]
train_lengths = d['train/trainlengths'][:]
final_test_seq = d['test/testdata'][:]
test_lengths = d['test/testlengths'][:]

print "sum(train_lengths) = ", sum(train_lengths)
print "final_train_seq.shape = ", final_train_seq.shape
print "sum(test_lengths) = ", sum(test_lengths)
print "final_test_seq.shape = ", final_test_seq.shape

for st in range(12, 20):
    print "Creating process for states = ", str(st)
    p = Process(target=train_hmm, args=(st, final_train_seq, train_lengths, final_test_seq, test_lengths))
    p.start()
    p.join(5)








