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
import argparse

warnings.filterwarnings('ignore')

parser = argparse.ArgumentParser()
parser.add_argument('--data_file', \
                    help='The compressed hdf5 train/dev/test data for HMM', \
                    default='data/hmm_data.hdf5')
parser.add_argument('--output_dir', \
                    help='Directory to save the trained models and the model scores', \
                    default='results/')
args, unknown = parser.parse_known_args()

data_file = args.data_file
output_dir = args.output_dir

try:
    os.makedirs(output_dir)
except:
    pass

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

results_file = os.path.join(output_dir, 'results.csv')

if os.path.isfile(results_file):
    f = open(results_file,'a')
    writer = csv.writer(f)
else:
    f = open(results_file,'w')
    writer = csv.writer(f)
    writer.writerow(['Timestamp','Fit time','Score time','Model','Covariance','No. of States','Train Score','Test Score','Convergence'])

for st in range(10, 16):
    nstates=st
    covartype="diag"
    modeltype="GaussianHMM"

    model=hmm.GaussianHMM(n_components=nstates, n_iter=500, covariance_type=covartype, verbose=True, tol=0.1)
    print "Training "+str(nstates)+" states"
    start_time = time.time()
    model = model.fit(final_train_seq,train_lengths)
    print "Fitting Done"
    fittingtime = (time.time()-start_time)/60
    start_time = time.time()
    print "Calculating the score"
    trainscore = model.score(final_train_seq, lengths=train_lengths)
    testscore = model.score(final_test_seq, lengths=test_lengths)
    scoringtime = (time.time()-start_time)/60
    print "Scoring done"
    writer.writerow([str(datetime.datetime.now()),fittingtime,scoringtime,modeltype,covartype,nstates, trainscore, testscore,
                     model.monitor_.iter])


    dir_to_save = os.path.join(output_dir, modeltype + covartype)
    file_path = os.path.join(dir_to_save, str(nstates) + 'states') 

    try:
        os.makedirs(dir_to_save)
    except:
        pass

    joblib.dump(model,file_path)

f.close()
d.close()








