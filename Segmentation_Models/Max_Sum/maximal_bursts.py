'''
Implementation of the All-Maximal Sum segments linear time algorithm described in paper:
Ruzzo, Walter L., and Martin Tompa. "A linear time algorithm for finding all maximal scoring subsequences.
Also implementing the extension to this according to the paper:Lappas, Theodoros, et al. "On burstiness-aware search for document sequences." 
This is used to find the maximal sum bursts given the project scores

Input: Pickle of project:burst_scores dictionary
Output: Maximal Sum Segments of the given scores per project pickled as dictionary
'''

import os
import sys
import collections
import csv
import cPickle as pickle
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--burst_score_pickle', help='The pickled file containing project-wise burst scores')
parser.add_argument('--output_file', help='Output filename for the maximal bursts')
args, unknown = parser.parse_known_args()

burst_score_pickle = args.burst_score_pickle
output_file = args.output_file

# NamedTuple for storing the Lj, Rj and the interval indexes of the algorithm
left_right_values = collections.namedtuple('left_right_values', 'left right start_idx end_idx')

def MAX_1(K):
    find_interval_flag = True   # True indicates that a new subinterval has to be found and the previous intervals are done
    n = len(K)
    i = -1
    running_sum = 0
    max_seq_list = []
    L_R_val_list = []
    cur_interval = ()
    cur_left = -1
    cur_right = -1

    while (i < n):
        # The processing of all the previous Ijs is done. Process a new number
        if find_interval_flag == True:
            i += 1
            if i>= n:
                break
            num = K[i]
            if num >= 0:
                cur_interval = (num,)
                cur_left = running_sum
                cur_right = running_sum + num
                find_interval_flag = False
            running_sum += num

        else:
            l_r_len = len(L_R_val_list)
            l_r_tuple = left_right_values(left=cur_left, right=cur_right, start_idx=i, end_idx=i)

            # First Entry
            if len(max_seq_list) == 0 and len(L_R_val_list) == 0:
                max_seq_list.append(cur_interval)
                L_R_val_list.append(l_r_tuple)
                find_interval_flag = True

            # Main ALgorithm
            else:
                j_found = False
                L_j = -1
                R_j = -1
                j = 0
                
                # Algo Step 1
                for j in range(l_r_len-1, -1, -1):
                    L_j = L_R_val_list[j].left
                    R_j = L_R_val_list[j].right
                    if L_j < cur_left:
                        j_found = True
                        break

                # Algo Step 2 and 3
                if j_found == False or R_j >= cur_right:
                    max_seq_list.append(cur_interval)
                    if len(L_R_val_list) < len(max_seq_list):
                        L_R_val_list.append(l_r_tuple)
                    find_interval_flag = True

                # Algo Step 4
                else:
                    if R_j >= cur_right:
                        print "Something went wrong"
                        return cur_interval, cur_left, cur_right, find_interval_flag
                    else:
                        # Extend the current subsequence to the left till the leftmost score in Ij
                        l_r_j = L_R_val_list[j]
                        cur_interval = tuple(K[l_r_j.start_idx:i+1])
                        cur_left = l_r_j.left
                        del L_R_val_list[j:]
                        del max_seq_list[j:]
                        
                        # Update LR list only if not already added
                        new_lr = left_right_values(left=l_r_j.left, right=cur_right, start_idx=l_r_j.start_idx, end_idx=i)
                        if j < len(L_R_val_list):
                            L_R_val_list[j] = new_lr
                        else:
                            L_R_val_list.append(new_lr)

                        find_interval_flag = False
    return max_seq_list, L_R_val_list

def MAX_2(seq_list, lr_list):
    second_max_list = []
    second_lr_list = []
    for seq,lr in zip(seq_list, lr_list):
        arr = list(seq)
        original_start = lr.start_idx
        max_seq, lr_seq = MAX_1(arr)
        lr_seq = [left_right_values(left=x.left, right=x.right, start_idx=x.start_idx+original_start, end_idx=x.end_idx+original_start) for x in lr_seq]
        second_max_list.extend(max_seq)
        second_lr_list.extend(lr_seq)
    return second_max_list, second_lr_list

burst_score_dict = pickle.load(open(burst_score_pickle, 'rb'))
projects = burst_score_dict.keys()
final_dict = {}

for project in projects:
    print "Processing for the project: ", project
    scores = burst_score_dict[project]
    print "Calculating first level of maximal intervals"
    first_level_intervals, first_lr = MAX_1(scores)
    print "Calculating second level of maximal intervals"
    second_level_intervals,second_lr = MAX_2(first_level_intervals, first_lr)
    bursts = [(x.start_idx, x.end_idx) for x in second_lr]
    final_dict[project] = bursts

with open(output_file, 'wb') as p_pickle:
    pickle.dump(final_dict, p_pickle)






