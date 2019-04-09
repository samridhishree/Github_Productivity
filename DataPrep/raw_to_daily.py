'''
Creates some summary files of the raw data
'''

import os
import sys
import csv
import glob
import calendar
from collections import defaultdict
from datetime import datetime
import pdb
import argparse

csv.field_size_limit(sys.maxsize)


parser = argparse.ArgumentParser()
#parser.add_argument('--aliases', help='list of csv files, each containing (provenance, alias1, alias2)',
#                default='DataPrep/aliases_prs.csv,DataPrep/aliases_pushes.csv')
parser.add_argument('--raw_commits_dir', help='Folder containing raw_commits',
                default='Sample_Data/congruence/raw_commits/')
parser.add_argument('--raw_issues_dir', help='Folder containing raw issues',
                default='Sample_Data/congruence/raw_issues/')
parser.add_argument('--participation', help='participation counts',
                default='Sample_Data/HMM/participation2.csv')
parser.add_argument('--daily_data', help='daily activity counts per project',
                default='Sample_Data/HMM/daily_data2/')
args, unknown = parser.parse_known_args()

def mkdirp(d):
    try:
        os.makedirs(d)
    except:
        pass

def strip_underscore(prjname, kount):
    return "_".join(prjname.split("_")[:-kount])
def tilde_to_slash(prjname):
    return prjname.replace("~","/").lower()
def strip_suffix(prjname, suffix):
    prjname = prjname.strip()
    assert prjname[-len(suffix):] == suffix, "Project " + prjname + " does not end in " + suffix
    return prjname[:-len(suffix)]

#aliases = defaultdict(set)
#def read_aliases(fn):
    #for row in csv.DictReader(open(fn)):
        #ghname = row["alias1"]
        #email = row["alias2"]
        #if "@" in ghname and not "@" in email:
            #(email,ghname) = (ghname,email)
        #if "@" in email and not "@" in ghname:
            #aliases[email].add(ghname)
#
#for fn in args.aliases.split(","):
    #read_aliases(fn)
#for alias in aliases.keys():
    ##if len(aliases[alias]) > 1: 
        ##print "Discarding ambiguous ", alias, aliases[alias]
        ##del aliases[alias]
    ##else:
    #aliases[alias] = list(aliases[alias])[0]

#print "Identified", len(aliases), "such as", aliases.keys()[0], aliases[aliases.keys()[0]]
mkdirp(args.daily_data)

#commits
#"rectype","issueid","project_owner","project_name","actor","time","text","action","title","provenance","paths","plus_1","
#urls","issues","userref","code"
#"commit_messages","","0101","pipetools","0101","2013-02-10 17:51:50","Release 0.2.1","0142ee7da27a38fccce704d5b0275d8f4dc
#88e95","","api.github.com,git_clone","[u'[""pipetools/__init__.py"", ""changelog.rst""]']","False","[]","[]","[]","[]"
#
#
#issues
#"rectype","issueid","project_owner","project_name","actor","time","text","action","title"
#"issue_title","1","0101","pipetools","pjz","2016-07-25 16:54:42","Any chance you want to upgrade this to support python3?
#","start issue","No python3 support"
#
#
#daily_data/zulko~unroll
#project,period,commit_messages,pull_request_merged,issue_comment,commit_comments,issue_title,issue_closed,pull_request_title,pull_request_commit_comment,pull_request_commit
#zulko~unroll,20140223,1,0,0,0,0,0,0,0,0
#
#
#participation.csv
#owner,project,actor,first_participation_date,first_participation_action,first_member_date,first_member_action
#0101,pipetools,0101,2012-09-25T18:49:37,commit_messages,2012-09-25T18:49:37,owner
#0101,pipetools,Arnie97,2016-07-28T17:01:02,pull_request_commit,2016-07-28T17:01:02,pull_request_commit

def update_actor(info, time, rectype, actor, owner, acts=None):
    if acts is not None and rectype not in acts and actor != owner: return
    daterec = "first_participation_date" if acts is None else "first_member_date"
    actrec = "first_participation_action" if acts is None else "first_member_action"
    if info[actor][daterec] == "" or info[actor][daterec] > time or actor==owner:
        oldact = info[actor].get(actrec)
        if actor == owner: rectype="owner"
        info[actor][actrec] = rectype
        info[actor][daterec] = time

projects = \
     set([strip_underscore(f,1) for f in os.listdir(args.raw_issues_dir)]).union(
     set([strip_suffix(f, "_commits.csv") for f in os.listdir(args.raw_commits_dir)]))

print "Going to convert", len(projects),"projects"
participationcsv = csv.writer(open(args.participation,"w"))
participationflds = "owner,project,actor,first_participation_date,first_participation_action,first_member_date,first_member_action".split(",")
dailyflds = "project,period,commit_messages,pull_request_merged,issue_comment,commit_comments,issue_title,issue_closed,pull_request_title,pull_request_commit_comment,pull_request_commit".split(",")
participationcsv.writerow(participationflds)
memberactions = ["pull_request_merged","commit_messages","pull_request_commit_comment"]
for ix, project in enumerate(sorted(projects)):
    print ix, project
    owner = project.split("~")[0]
    pname = project.split("~")[1]
    dailycsv = csv.writer(open(args.daily_data + "/" + project + ".csv", "w"))
    dailycsv.writerow(dailyflds)

    dayinfo = defaultdict(lambda: defaultdict(int))  #  YYYYMMDD -> { rectype -> count }
    actorinfo = defaultdict(lambda: defaultdict(str))  # actor -> four fields
    commitfile = args.raw_commits_dir + "/" + project + "_commits.csv"
    if os.path.isfile(commitfile):
      for row in csv.DictReader(open(commitfile)):
        thedate = row["time"][0:4] + row["time"][5:7] + row["time"][8:10]
        dayinfo[thedate][row["rectype"]] += 1
        #row["actor"] = aliases.get(row["actor"],row["actor"])
        update_actor(actorinfo, row["time"], row["rectype"], row["actor"], owner)
        update_actor(actorinfo, row["time"], row["rectype"], row["actor"], owner, acts=memberactions)
    for issuefile in glob.glob(args.raw_issues_dir + "/" + project + "_issue*.csv"): # glob:
        for row in csv.DictReader(open(issuefile)):
            thedate = row["time"][0:4] + row["time"][5:7] + row["time"][8:10]
            dayinfo[thedate][row["rectype"]] += 1
            #row["actor"] = aliases.get(row["actor"],row["actor"])
            update_actor(actorinfo, row["time"], row["rectype"], row["actor"], owner)
            update_actor(actorinfo, row["time"], row["rectype"], row["actor"], owner, acts=memberactions)
        
    for day in dayinfo:
        dailycsv.writerow([project,day] + \
             [dayinfo[day][rectype] for rectype in dailyflds[2:]])

    for actor in actorinfo:
        participationcsv.writerow([owner,pname,actor, \
             actorinfo[actor]["first_participation_date"],
             actorinfo[actor]["first_participation_action"],
             actorinfo[actor]["first_member_date"],
             actorinfo[actor]["first_member_action"]])
