import csv
import argparse
from collections import defaultdict
import pickle
import datetime
from dateutil.parser import parse

parser = argparse.ArgumentParser("Examine individual congruence in a burst")
parser.add_argument("--project", help="Project owner <underscore> name", default="nilearn_nilearn")
parser.add_argument("--burstid", help="Burst number", default="88")
parser.add_argument("--data_dir", help="Where intermediate congruence files are stored",
         default = "Sample_Data/congruence/congruence_outputs/output_requirements")
args, unknown = parser.parse_known_args()

def median(lst):
    if len(lst) == 0: return None
    if len(lst) == 1: return lst[0]
    sx = sorted(lst)
    if len(lst) % 2 == 1:
        median=sx[len(lst)/2]
    else:
        median=(sx[int(len(lst)/2-1)] + sx[int(len(lst)/2)])/2.0
    return median

assert median([]) is None
assert median([3]) == 3
assert median([1,2,3,4,5]) == 3
assert median([1,2,3,4]) == 2.5, median([1,2,3,4])


def analyze_congruence(project, burstid, data_dir, burst_dates):
    filebase = data_dir + "/" + project + "_burst_" + burstid 
    actual_mr = defaultdict(lambda: defaultdict(float))
    requirements = defaultdict(lambda: defaultdict(float))
    actual_mod = defaultdict(lambda: defaultdict(float))
    dr = csv.DictReader(open(filebase + "_actual_mr.csv"))
    for row in dr:
        for col in dr.fieldnames[1:]:
            actual_mr[row['']][col] = float(row[col])
    dr = csv.DictReader(open(filebase + "_requirements.csv"))
    for row in dr:
        for col in dr.fieldnames[1:]:
            requirements[row['']][col] = float(row[col])
    #dr = csv.DictReader(open(filebase + "_actual_mod.csv"))
    #for row in dr:
        #for col in dr.fieldnames[1:]:
            #actual_mod[row['']][col] = float(row[col])
    
    numerator_tally = 0
    denom_tally = 0
    print "For burst", project, burstid, burst_dates
    burst_dates = map(parse, burst_dates.split("-"))
    burst_dates[1] += datetime.timedelta(days=1)
    print "           (", burst_dates,")"
    for person in actual_mr:
        print "========"
        buddies = [p for p in actual_mr[person] if actual_mr[person][p] > 0.0 and p != person]
        coworkers = [p for p in requirements[person] if requirements[person][p] > 0.0 and p != person]
        missing = set(coworkers).difference(set(buddies))
        excess = set(buddies).difference(set(coworkers))
        numerator_tally += len(coworkers) - len(missing)
        denom_tally += len(coworkers)
        print person, "congruence was ", float(len(buddies))/len(coworkers), "(", len(buddies),"/",len(coworkers),")"
        print "     ....talked to", buddies
        if len(missing) > 0:
            print "     ....should also have talked to ", missing
        if len(excess) > 0:
            print "     ....wasn't predicted to need to talk to ", excess

    commitfn = "Sample_Data/congruence/burst_commits/" + \
          project.replace("_","~",1) + "_burst_" + str(burstid) + "_commits.csv"
    issuesfn = "Sample_Data/congruence/burst_issues/" +  \
         project.replace("_","~",1) + "_burst_" + str(burstid) + "_issues.csv"
    iss = defaultdict(lambda: defaultdict(int))
    iss_outside = defaultdict(lambda: defaultdict(int))
    for irow in csv.DictReader(open(issuesfn)):
        t = parse(irow["time"])
        if t >= burst_dates[0] and t< burst_dates[1]:
            iss[irow["issueid"]][irow["actor"]] += 1
        else:
            iss_outside[irow["issueid"]][irow["actor"]] += 1
       
    for issue in sorted(set(iss.keys()).union(set(iss_outside.keys()))):
        print "Issue",issue,iss.get(issue,"[]")
        print "           (outside of range:", iss_outside.get(issue,"[]"), ")"

    print "Total congruence = ", numerator_tally, "/", denom_tally, "=", float(numerator_tally)/denom_tally

        #medianreq = median([r for r in requirements[person].values()])
        #for bud in buddies:
            #print "Talked to", bud, "amount", actual_mr[person][bud], "which was", \
                #"warranted" if requirements[person][bud] > medianreq else "unwarranted", \
                #"(req = ", requirements[person][bud], "/", medianreq,")"


bursts = pickle.load(open("Sample_Data/HMM/results/daily_bursts.pickle","rb"))
analyze_congruence(args.project, args.burstid, args.data_dir, bursts[args.project.replace("_","~",1)][int(args.burstid)])
