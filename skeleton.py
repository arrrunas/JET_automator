# coding: utf-8

import pandas as pd
import numpy as np
import re
from sys import argv

# filename is specified as script argument, usage: python jet_automator.py filename.csv
script, filename = argv

# import tasks are run
print '*'*50
print '\nImporting %r. Plese specify column separator and press enter. Example what to type: ,' % filename
separator = raw_input("> ")
data = pd.read_csv(filename, error_bad_lines=False, sep=separator)
print 'Import succesful. Following columns imported:\n'
print data.columns
print '*'*50
print '\nSample data:'
print data.head()

# data cleaning to rename columns and remove currency symbols
def data_cleaning(data):
    data_cleaned = data.rename(columns={'Account number':'ACC', 'Credit': 'CR', 'Debit': 'DR'})
    data_cleaned['CR'] = data_cleaned.CR.replace('[\$,)]', '', regex=True).astype(float)
    data_cleaned['DR'] = data_cleaned.DR.replace('[\$,)]', '', regex=True).astype(float)
    data_cleaned['CR'] = data_cleaned.CR.replace('[\€,)]', '', regex=True).astype(float)
    data_cleaned['DR'] = data_cleaned.DR.replace('[\€,)]', '', regex=True).astype(float)
    return data_cleaned

# completeness test: group by account name and show sum of CR/DR
def completeness_test(data_cleaned):
    completeness = data_cleaned.groupby(['ACC']).agg({'CR':'sum','DR':'sum'})
    completeness.to_csv(r'completeness.txt', sep=';', mode='a')
    print '*'*50
    print "\nCompleteness test completed in completeness.txt."

def cr_dr_test(data_cleaned):
    cr_dr = data_cleaned.agg({'CR':'sum', 'DR':'sum'})
    cr_dr.to_csv(r'cr_dr.txt', sep=';', mode='a')
    print '*'*50
    print "\nCredits=Debits test completed in cr_dr.txt."

data_cleaned = data_cleaning(data)
completeness_test(data_cleaned)
