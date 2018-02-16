'''
Combines all the issue data for each project along with the comment text.
The fields kept in the final csv: project, date, rectype, text(clean)
'''

import os
import sys
import csv
import codecs
import glob
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import cPickle as pickle
import re
import string
import argparse

csv.field_size_limit(sys.maxsize)
reload(sys)
sys.setdefaultencoding('utf-8')

parser = argparse.ArgumentParser()
parser.add_argument('--clean_issue_dir', help='Directory with clean issue threads')
parser.add_argument('--commits_dir', help='Directory containing project commits')
parser.add_argument('--output_dir', help='Directory to store the output csv containing commits and issues with stemmed words')
args, unknown = parser.parse_known_args()

clean_issue_dir = args.clean_issue_dir
commits_dir = args.commits_dir
output_dir = args.output_dir
MAX_LEN = 400

def CleanText(text):
    text = str(text)
    i=text.find('~~')    
    while (i>=0):
        endi=i+2+text[i+2:].find('~~')
        if endi==i+1: text=text[:i]
        else: text=text[:i]+text[endi+2:]
        i=text.find('~~')

    #Remove code snippets
    i=text.find('```')
    while (i>=0):
        endi=i+3+text[i+3:].find('```')
        if endi==i+2:
            text=text[:i]
        else:
            text=text[:i]+' {code} '+text[endi+3:]
        i=text.find('```')

    i=text.find('`')
    while (i>=0):
        endi=i+1+text[i+1:].find('`')
        if endi==i:
            text=text[:i]
        else:
            text=text[:i]+' {code} '+text[endi+1:]
        i=text.find('`')

    i=text.find('>')
    while (i>=0):
        endi=i+text[i:].find('\n')
        if endi==i-1: text=text[:i]
        else: text=text[:i]+text[endi+1:]
        i=text.find('>')

    #Find and extract URLs
    text = re.sub(r'http\S+', '{url}', text, flags=re.MULTILINE)
    
    # Remove {url} and {code} tags
    text = text.replace('{url}', '')
    text = text.replace('{code}', '')

    # Strip punctuation
    text = text.translate(None, string.punctuation)

    text=text.replace('*','')
    text=text.replace('[','')
    text=text.replace(']','')
    text=text.replace('(','')
    text=text.replace(')','')
    text=text.replace('{','')
    text=text.replace('}','')
    text=text.replace('\\',' ')
    text=text.replace('<',' ')
    text=text.replace('>',' ')
    text=text.replace('`',' ')
    text=text.replace('"',' ')
    text = text.replace('\n', ' ').replace('\r', '')    

    #Remove non utf-8 characters and restrict the length
    text=text.decode('utf-8','ignore').encode("utf-8")
    words = text.split()
    if len(words) > MAX_LEN:
        words = words[:MAX_LEN]
    
    #Remove stopwords and stem
    ps = PorterStemmer()
    filtered_words = [word for word in words if word not in stopwords.words('english')]
    stemmed_words = [ps.stem(word) for word in filtered_words]
    lower_words = [word.lower() for word in stemmed_words]
    text = ' '.join(stemmed_words)

    return text

#for project in projects:
for commit_filename in os.listdir(commits_dir):
    project = commit_filename.split('_commits.csv')[0]
    print "Processing for project: ", project
    issue_pattern = clean_issue_dir + '*' + project + '*.csv'
    isuue_files = glob.glob(issue_pattern)
    if len(isuue_files) == 0:
        print "No issue files found aborting"
        continue
    commit_file = os.path.join(commits_dir, commit_filename)

    output_file = os.path.join(output_dir, project + '_issue_comment.csv')
    w = codecs.open(output_file, 'wb', encoding='utf-8')
    writer = csv.writer(w)
    writer.writerow(['time', 'rectype', 'text'])

    # Write the issue data
    for issue_file in isuue_files:
        data = pd.read_csv(issue_file)
        df_comment = data.loc[data['rectype'].str.find('comment')>0]
        df_title = data.loc[data['rectype'].str.find('title')>0]
        df = pd.concat([df_comment, df_title])
        df.fillna('', inplace=True)
        df_non_repeat = df.drop_duplicates(subset=['clean_text'], keep='first')
        for index,row in df_non_repeat.iterrows():
            to_write = [row['time'], row['rectype'], row['clean_text']]
            writer.writerow(to_write)

    # Write commit data
    c_data = pd.read_csv(commit_file)
    for index,row in c_data.iterrows():
        clean_text = CleanText(row['text'])
        to_write = [row['time'], row['rectype'], clean_text]
        writer.writerow(to_write)
    w.close()







