vardir=Sample_Data/variants/week_bursts/
bpickle=${vardir}/short_bursts.pickle
samdir=/usr2/scratch/sschoudh/kdd_v6/congruence/
##python Variants/shorter_bursts.py --burst_pickle /usr2/scratch/sschoudh/pypi_data_v6/hmm_bursts/hmm_bursts_mongo_counts.pickle --shortened_burst_pickle Sample_Data/HMM/results/shortened_bursts.pickle --number_of_bursts 1000 --shortest_burst_to_break 1 --new_burst_length 1
#python Variants/shorter_bursts.py --burst_pickle=/usr2/scratch/sschoudh/pypi_data_v6/hmm_bursts/hmm_bursts_mongo_counts.pickle --shortened_burst_pickle=$bpickle --number_of_bursts=1000 --shortest_burst_to_break=180 --new_burst_length=7
#python Coordination_Models/extract_burst_commits.py --raw_commits_dir /usr2/scratch/sschoudh/pypi_data_v6/raw_commits_from_mongo --output_dir ${vardir}/congruence/burst_commits --burst_pickle $bpickle
#python Coordination_Models/extract_burst_issues.py --issue_dir /usr2/scratch/sschoudh/pypi_data_v6/raw_issues_from_mongo --output_dir ${vardir}/congruence/burst_issues --burst_pickle $bpickle 

#python Coordination_Models/people_component_experience.py --raw_commit_path /usr2/scratch/sschoudh/pypi_data_v6/raw_commits_from_mongo/ --project_bursts_pickle $bpickle --output_pickle_path ${vardir}/component_experience/

# NB:  There's a co_commit_adj_pickle directory (with a name something like that) that's  a dictionary from (file1,file2) -> count
#      but there's also a co_commit_adj directory aka reformatted_adj directory, that imports that into a data frame.  Use the latter
#
#python Coordination_Models/burst_congruence.py --fct_adjacency_dir $samdir/reformatted_adj/ --user_file_pickle_dir $samdir/user_file_dict/ --user_mod_fct $samdir/user_module_dict/ --bursty_commits_dir ${vardir}/congruence/burst_commits/ --bursty_issues_dir ${vardir}/congruence/burst_issues/ --project_bursts_pickle $bpickle --file_mod_pickle_dir $samdir/file_module_dict/ --user_experience_pickle_dir $vardir/component_experience/ --participation_csv /usr2/scratch/sschoudh/kdd_v6/HMM/data/participation.csv --output_csv_dir ${vardir}/congruence_outputs/output_csv/ --output_csv_req_metrics ${vardir}/congruence_outputs/output_requirements/

python Coordination_Models/combine_congruence_data.py --congruence_dir ${vardir}/congruence_outputs/output_csv/ --output_file ${vardir}/congruence_outputs/regression_table.csv

#parser = argparse.ArgumentParser()
#parser.add_argument('--fct_adjacency_dir', help='Directory containing 2D adjacency matrix (output of: reformat_adjacency.py)',\
    #default='Sample_Data/congruence/co_commit_adj/')
#parser.add_argument('--user_file_pickle_dir', help='Directory containing the user-file membership (output of: people_file_dict.py)',\
    #default='Sample_Data/congruence/user_file_dict/')
#parser.add_argument('--user_mod_fct', help='Directory containing user module membership (output of: people_module_dict.py)',\
    #default='Sample_Data/congruence/user_module_dict/')
#parser.add_argument('--bursty_commits_dir', help='Directory containing the per project per burst commits (output of: extract_burst_commits.py)',\
    #default='Sample_Data/congruence/burst_commits/')
#parser.add_argument('--bursty_issues_dir', help='Directory containing active issues per burst per project (output of: extract_burst_issues.py)',\
    #default='Sample_Data/congruence/burst_issues/')
#parser.add_argument('--project_bursts_pickle', help='Pickled list of bursts per project (output of: HMM/extract_daily_bursts.py)',\
    #default='Sample_Data/HMM/results/daily_bursts.pickle')
#parser.add_argument('--file_mod_pickle_dir', help='Directory containing the file module membership (output of: file_module_dict.py)',\
    #default='Sample_Data/congruence/file_module_dict/')
#parser.add_argument('--user_experience_pickle_dir', help='Directory containing component experience \
    #per user for each project (output of: people_component_experience.py)',\
    #default='Sample_Data/congruence/component_exp/')
#parser.add_argument('--participation_csv', help='Input csv file containing the participation information for the users of the project',\
    #default='Sample_Data/HMM/participation.csv')
#parser.add_argument('--output_csv_dir', help='Output directory to hold project wise computed metrics for each burst',\
    #default='Sample_Data/congruence/congruence_outputs/output_csv/')
#parser.add_argument('--output_pickle_dir', help='Output directory to hold te computed metric as pickled dataframes',\
    #default='Sample_Data/congruence/congruence_outputs/output_pickle/')
#parser.add_argument('--output_csv_req_metrics', help='Output directory to hold the requirement matrices',\
    #default='Sample_Data/congruence/congruence_outputs/output_requirements/')
