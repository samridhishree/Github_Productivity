print(getwd())
#setwd('/usr2/scratch/sschoudh/alternate_burst/klein')
library("bursts", lib.loc="/usr2/scratch/sschoudh/rlib")
project_offsets_folder <- "offsets_per_project/"
output_folder <- "burst_output/"
#print(output_folder)
file_list <- list.files(path=project_offsets_folder, pattern="*.csv")
#print(file_list)

# Iterate over the offsets
for (i in 1:length(file_list)){
	cur_file <- paste(project_offsets_folder, file_list[i], sep="")
	print(cur_file)
	project_name <- strsplit(cur_file, ".csv")[1]
	project_name <- project_name[[1]]
	data <- read.csv(cur_file, stringsAsFactors=FALSE)
	offsets <- data['offset']
	formatted_offset <- unlist(offsets)
	bursts <- kleinberg(formatted_offset)
	output_file <- paste(output_folder, file_list[i], sep="")
	write.csv(bursts, file=output_file)
	}
