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
    print "Please specify name of the column containing transaction ID."
    trans_ID = raw_input('> ')
    print "Please specify name of the column containing user ID."
    user_ID = raw_input('> ')
    print "Please specify name of the column containing posting date."
    post_date = raw_input('> ')
    print "Please specify name of the column containing entry date."
    entry_date = raw_input('> ')

    # test if amounts are in single column or not
    single_column_amount = False
    if debit == credit:
        single_column_amount = True
        data_cleaned = data.rename(columns={acc_no:'Account no', debit: 'Amount',\
            trans_ID: 'Transaction ID', user_ID: 'User ID',\
            post_date:'Posting date', entry_date:'Entry date'})
        data_cleaned['Amount'] = data_cleaned.Amount.str.strip()
        data_cleaned['Amount'] = data_cleaned.Amount.replace('[\$,)]', '', regex=True)
        data_cleaned['Amount'] = data_cleaned.Amount.replace('[\€,)]', '', regex=True)
        data_cleaned['Amount'] = data_cleaned.Amount.replace('[\EUR,)]', '', regex=True).astype(float)
    else:
        data_cleaned = data.rename(columns={acc_no:'Account no', credit: 'Credit',\
            debit: 'Debit', trans_ID: 'Transaction ID', user_ID: 'User ID',\
            post_date:'Posting date', entry_date:'Entry date'})
        data_cleaned['Credit'] = data_cleaned.Credit.str.strip()
        data_cleaned['Debit'] = data_cleaned.Debit.str.strip()
        data_cleaned['Credit'] = data_cleaned.Credit.replace('[\$,)]', '', regex=True)
        data_cleaned['Debit'] = data_cleaned.Debit.replace('[\$,)]', '', regex=True)
        data_cleaned['Credit'] = data_cleaned.Credit.replace('[\€,)]', '', regex=True)
        data_cleaned['Debit'] = data_cleaned.Debit.replace('[\€,)]', '', regex=True)
        data_cleaned['Credit'] = data_cleaned.Credit.replace('[\EUR,)]', '', regex=True).astype(float)
        data_cleaned['Debit'] = data_cleaned.Debit.replace('[\EUR,)]', '', regex=True).astype(float)
    
    print '*'*50
    print '\nData cleaning completed. Columns identified as follows:\n'
    print data_cleaned.columns
    return data_cleaned

data_cleaning(data)