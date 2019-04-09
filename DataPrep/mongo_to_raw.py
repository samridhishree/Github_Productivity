from pymongo import MongoClient
from collections import defaultdict
import os
import argparse
import csv

client = MongoClient("mongodb://127.0.0.1:27017")
project_events = client["pypi-v6"].project_events
issue_events = client["pypi-v6"].issue_events


parser = argparse.ArgumentParser()
parser.add_argument('--raw_commits_dir', help='Folder containing raw_commits',
                default='Sample_Data/congruence/raw_commits/')
parser.add_argument('--raw_issues_dir', help='Folder containing raw issues',
                default='Sample_Data/congruence/raw_issues/')
parser.add_argument('--aliases', help='list of csv files, each containing (provenance, alias1, alias2)',
                default='DataPrep/aliases_prs.csv,DataPrep/aliases_pushes.csv')
args, unknown = parser.parse_known_args()


#   make an alias map from alias files
#   this is aggressive, picking arbitrarily one github id to use
#   for an email even if more than one match; in most cases this seems
#   pretty good
aliases = defaultdict(set)
def read_aliases(fn):
    for row in csv.DictReader(open(fn)):
        ghname = row["alias1"]
        email = row["alias2"]
        if "@" in ghname and not "@" in email:
            (email,ghname) = (ghname,email)
        if "@" in email and not "@" in ghname:
            aliases[email].add(ghname)

for fn in args.aliases.split(","):
    read_aliases(fn)
for alias in aliases.keys():
    #if len(aliases[alias]) > 1:
        #print "Discarding ambiguous ", alias, aliases[alias]
        #del aliases[alias]
    #else:
    aliases[alias] = list(aliases[alias])[0]

print "Identified", len(aliases), "such as", aliases.keys()[0], aliases[aliases.keys()[0]]




#  Make directories we need
#
#

try:
    os.makedirs(args.raw_commits_dir)
except:
    pass

try:
    os.makedirs(args.raw_issues_dir)
except:
    pass

def sanitize(k):
    try:
       return k.encode("utf-8","default")
    except:
       return str(k)

prev = ""
outf = None
outcsv = None
flds =["rectype","issueid","project_owner","project_name","actor","time","text","action","title","provenance","paths","plus_1","urls","issues","userref","code"]
for row in project_events.find().sort([("project_owner_lower", 1), 
                                       ("project_name_lower", 1),
                                       ("time", 1)]):
    proj = row["project_owner_lower"] + "~" + row["project_name_lower"]
    if prev != proj:
        print proj
        if outf is not None:
            outf.close()
        outf = open(os.path.join(args.raw_commits_dir, proj + "_commits.csv"), "w")
        outcsv = csv.writer(outf, quoting=csv.QUOTE_ALL)
        outcsv.writerow(flds)
        prev = proj
    
    row["actor"] = aliases.get(row["actor"],row["actor"])
    outcsv.writerow([sanitize(row.get(fld,"")) for fld in flds])
    
prev = ""
outf = None
outcsv = None
flds = ["rectype","issueid","project_owner","project_name","actor","time","text","action","title"]
for row in issue_events.find().sort([("project_owner_lower", 1), 
                                     ("project_name_lower", 1),
                                     ("issueid", 1),
                                     ("time", 1)]):
    proj = row["project_owner_lower"] + "~" + row["project_name_lower"] + "_issue" + str(row["issueid"])
    if prev != proj:
        print proj
        if outf is not None:
            outf.close()
        outf = open(os.path.join(args.raw_issues_dir, proj +".csv"), "w")
        outcsv = csv.writer(outf, quoting=csv.QUOTE_ALL)
        outcsv.writerow(flds)
        prev = proj
    row["actor"] = aliases.get(row["actor"],row["actor"])
    outcsv.writerow([sanitize(row.get(fld,"")) for fld in flds])
