#p = map(lambda x: x.replace('[', '').replace(']','').replace('"','').strip(), parts)
#Usage: python CreateUserCommitDep.py <path_to_commit_csvs> <Path_for_output_csvs>
import os
import sys
import csv

csv.field_size_limit(sys.maxsize)

commit_root_dir = sys.argv[1]
output_dir = sys.argv[2]
title_row = ['rectype', 'project_owner', 'project_name', 'actor', 'time', 'commit_message', 'action', 'files_affected']
valid_column_ids = [0, 2, 3, 4, 5, 6, 7]

# Read the commit files one by one and process their data
for fileName in os.listdir(commit_root_dir):
	#Read the commit csv file
	if fileName.endswith('.csv'):
		print "Processing file: ", fileName
		f = open(os.path.join(commit_root_dir, fileName), 'rb')
		reader = csv.reader(f)
		next(reader, None)

		#Synthesise the appropriate output file name and write the title row
		output_filename = fileName[:5].replace("repo_", "") + fileName[5:].replace('_commits.csv','') + '_commitDep.csv'
		w = open(os.path.join(output_dir, output_filename), 'wb')
		writer = csv.writer(w, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
		writer.writerow(title_row)

		#Start writing the content iteratively
		for row in reader:
			to_write = list(row[i] for i in valid_column_ids)
			files_affected = row[10]
			parts = files_affected.split(',')
			file_list = map(lambda x: x.replace('[', '').replace(']','').replace('"','').strip(), parts)
			to_write += file_list
			writer.writerow(to_write)
		w.close()
		f.close()






