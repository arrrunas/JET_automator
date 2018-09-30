# coding: utf-8

import pandas as pd
import numpy as np
import re
from sys import argv

# filename is specified as script argument, usage: python jet_automator.py filename.csv
script, filename = argv

# import tasks are run
print '\n'
print '*'*80
print '\nImporting %r. Plese specify column separator and press enter. Example what to type: ,' % filename
separator = raw_input("> ")
data = pd.read_csv(filename, error_bad_lines=False, sep=separator)
print 'Import succesful. Following columns imported:\n'
print data.columns
print '\n'
print '*'*80
print '\nSample data:'
print data.head()
print '\n'

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

    print "\nCalculating."
    # test if amounts are in single column or not
    single_column_amount = False
    if debit == credit:
        single_column_amount = True
        data_cleaned = data.rename(columns={acc_no:'Account no', debit: 'Amount',\
            trans_ID: 'Transaction ID', user_ID: 'User ID',\
            post_date:'Posting date', entry_date:'Entry date'})
        data_cleaned['Amount'] = data_cleaned.Amount.replace('[\$,)]', '', regex=True)
        data_cleaned['Amount'] = data_cleaned.Amount.replace('[\€,)]', '', regex=True)
        data_cleaned['Amount'] = data_cleaned.Amount.replace('[\EUR,)]', '', regex=True).astype(float)
    else:
        data_cleaned = data.rename(columns={acc_no:'Account no', credit: 'Credit',\
            debit: 'Debit', trans_ID: 'Transaction ID', user_ID: 'User ID',\
            post_date:'Posting date', entry_date:'Entry date'})
        data_cleaned['Credit'] = data_cleaned.Credit.replace('[\$,)]', '', regex=True)
        data_cleaned['Debit'] = data_cleaned.Debit.replace('[\$,)]', '', regex=True)
        data_cleaned['Credit'] = data_cleaned.Credit.replace('[\€,)]', '', regex=True)
        data_cleaned['Debit'] = data_cleaned.Debit.replace('[\€,)]', '', regex=True)
        data_cleaned['Credit'] = data_cleaned.Credit.replace('[\EUR,)]', '', regex=True).astype(float)
        data_cleaned['Debit'] = data_cleaned.Debit.replace('[\EUR,)]', '', regex=True).astype(float)
    
    print '\n'
    print '*'*80
    print '\nData cleaning completed. Columns identified as follows:\n'
    print data_cleaned.columns
    return data_cleaned, single_column_amount

# completeness test: group by account name and show sum of CR/DR
def completeness_test(data_cleaned, single_column_amount):
    if single_column_amount == True:
        completeness = data_cleaned.groupby(['Account no']).agg({'Amount':'sum'})
    else:
        completeness = data_cleaned.groupby(['Account no']).agg({'Credit':'sum','Debit':'sum'})

    # write to file and complete
    completeness.to_csv(r'completeness.txt', sep=';', mode='a')
    print '\n'
    print '*'*80
    print "\nCompleteness test completed in completeness.txt."

# cr/dr test: sum all credits and debits
def cr_dr_test(data_cleaned, single_column_amount):
    if single_column_amount == True:
        debit = data_cleaned.Amount[data_cleaned.Amount > 0].sum()
        credit = data_cleaned.Amount[data_cleaned.Amount < 0].sum()
        data = {'Debits: ': [debit], 'Credits': [credit]}
        cr_dr = pd.DataFrame(data)
        # test result
        diff = abs(debit) - abs(credit)
        if diff == 0:
            result = 'passed'
        else:
            result = 'failed'
    else:
        debit = data_cleaned.Debit.sum()
        credit = data_cleaned.Credit.sum()
        data = {'Debits: ': [debit], 'Credits': [credit]}
        cr_dr = pd.DataFrame(data)
        # test result
        diff = abs(debit) - abs(credit)
        if diff == 0:
            result = 'passed'
        else:
            result = 'failed'

    # write to file and complete
    cr_dr.to_csv(r'cr_dr.txt', sep=';', mode='a')
    print '\n'
    print '*'*80
    print "\nCredits = Debits test completed in cr_dr.txt. Test %s with diff %d." % (result, diff)

def correspondence(data_cleaned, single_column_amount):
    more_correspondence = True
    while more_correspondence == True:
        print '\n'
        print '*'*80
        print '\nEnter type of correspondence to do (eg. revenue, cash, etc.) or \'q\' to quit.'
        type_of_correspondence = raw_input("> ")
        if type_of_correspondence == 'q':
            more_correspondence == False
            break
        else:
            print '\nPlease specify a list of %s GL accounts for correspondence, separated by spaces (eg. 50001 50002 50003 etc.).' % type_of_correspondence
            correspondence_accounts = raw_input("> ").split(' ')
            # create new column and mark accounts for which correspondence test will be performed
            data_cleaned['%s correspondence' % type_of_correspondence] = ""
            data_cleaned['%s correspondence details' % type_of_correspondence] = ""
            # notify user that work begins because it can take a long time
            print "\nCalculating - be patient."
            # launch loop to mark transactions as corresponding to a GL account, then remark original transactions \
            # as non-correspondence 
            for account in correspondence_accounts:
                account_transactions = data_cleaned.loc[data_cleaned['Account no'].astype(str) == str(account), 'Transaction ID']
                data_cleaned.loc[data_cleaned['Transaction ID'].isin(account_transactions), '%s correspondence' % type_of_correspondence] = 'correspondence'
                data_cleaned.loc[data_cleaned['Transaction ID'].isin(account_transactions), '%s correspondence details' % type_of_correspondence] = 'Corresponds to %s' % account
                data_cleaned.loc[data_cleaned['Account no'].astype(str) == str(account), '%s correspondence' % type_of_correspondence] = "%s" % type_of_correspondence
                correspondence = data_cleaned.loc[data_cleaned['%s correspondence' % type_of_correspondence] != ""]
   
        # complete and write to file
        correspondence = data_cleaned.loc[data_cleaned['%s correspondence' % type_of_correspondence] != ""]
        correspondence.to_csv(r'%s correspondence.txt' % type_of_correspondence, sep=';', mode='a')
        print '\n'
        print '*'*80
        print "\n%s correspondence test completed in %s correspondence.txt." % (type_of_correspondence, type_of_correspondence)

data_cleaned, single_column_amount = data_cleaning(data)

completeness_test(data_cleaned, single_column_amount)
cr_dr_test(data_cleaned, single_column_amount)
correspondence(data_cleaned, single_column_amount)