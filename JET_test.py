# coding: utf-8

import pandas as pd
import numpy as np
import re

# import tasks are run
print '*'*50
print '\nImporting.'
data = pd.read_csv("JET.csv", error_bad_lines=False, sep=';')
print 'Import succesful. Following columns imported:\n'
print data.columns
print '*'*50
print '\nSample data:'
print data.head()

# data cleaning to rename columns and remove currency symbols
def data_cleaning(data):
    print "Please specify name of the column containing account number."
    acc_no = raw_input('> ')
    print "Please specify name of the column containing debit amounts."
    debit = raw_input('> ')
    print "Please specify name of the column containing credit amounts."
    credit = raw_input('> ')

    # test if amounts are in single column or not
    single_column_amount = False
    if debit == credit:
        single_column_amount = True

    data_cleaned = data.rename(columns={acc_no:'ACC', credit: 'CR', debit: 'DR'})
    data_cleaned['CR'] = data_cleaned.CR.replace('[\$,)]', '', regex=True).astype(float)
    data_cleaned['DR'] = data_cleaned.DR.replace('[\$,)]', '', regex=True).astype(float)
    data_cleaned['CR'] = data_cleaned.CR.replace('[\€,)]', '', regex=True).astype(float)
    data_cleaned['DR'] = data_cleaned.DR.replace('[\€,)]', '', regex=True).astype(float)
    print '*'*50
    print '\nData cleaning completed. Columns identified as follows:\n'
    print data_cleaned.columns
    return data_cleaned

data_cleaning(data)