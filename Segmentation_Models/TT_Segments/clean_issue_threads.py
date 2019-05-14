'''
Clean and stem the issue thread texts from the raw issue files
'''

import os
import sys
import csv
import re
import string
import codecs
import pandas as pd
import cPickle as pickle
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import argparse

csv.field_size_limit(sys.maxsize)
reload(sys)
sys.setdefaultencoding('utf-8')

parser = argparse.ArgumentParser()
parser.add_argument('--raw_issue_dir', help='The directory containing raw issue files', 
                default='Sample_Data/congruence/raw_issues/')
parser.add_argument('--clean_issue_dir', help='Directory containing the clean issues', 
                default='Sample_Data/congruence/clean_issues/')
args, unknown = parser.parse_known_args()

raw_issue_dir = args.raw_issue_dir
clean_issue_dir = args.clean_issue_dir
MAX_LEN = 400

try:
    os.makedirs(clean_issue_dir)
except:
    pass

def CleanIssueComment(text):
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

for filename in os.listdir(raw_issue_dir):
    print "Processing for file = ", filename
    f = codecs.open(os.path.join(raw_issue_dir, filename), 'rb', encoding='utf-8')
    reader = csv.DictReader(f)
    header = reader.fieldnames + ['clean_text']
    output_file = os.path.join(clean_issue_dir, filename.replace('.csv', '_clean.csv'))
    w = codecs.open(output_file, 'wb', encoding='utf-8')
    writer = csv.DictWriter(w, fieldnames=header)
    writer.writeheader()
    for row in reader:
        clean_text = CleanIssueComment(row['text'])
        row['clean_text'] = clean_text
        writer.writerow(row)




