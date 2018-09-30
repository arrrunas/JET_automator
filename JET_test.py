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
    acc_no = 'Account number'
    print "Please specify name of the column containing debit amounts."
    debit = 'Debit'
    print "Please specify name of the column containing credit amounts."
    credit = 'Credit'
    print "Please specify name of the column containing transaction ID."
    trans_ID = 'Voucher'
    print "Please specify name of the column containing user ID."
    user_ID = 'User'
    print "Please specify name of the column containing posting date."
    post_date = "Posting date"
    print "Please specify name of the column containing entry date."
    entry_date = "Transaction date"

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
    
    print '\n'
    print '*'*80
    print '\nData cleaning completed. Columns identified as follows:\n'
    print data_cleaned.columns
    return data_cleaned, single_column_amount

# correspondence test loop
def correspondence(data_cleaned, single_column_amount):
    more_correspondence = True
    while more_correspondence == True:
        print '*'*80
        print '\nEnter type of correspondence to do (eg. revenue, cash, etc.) or \'q\' to quit.'
        type_of_correspondence = raw_input("> ")
        if type_of_correspondence == 'q':
            more_correspondence == False
            break
        else:
            print '\nPlease specify a list of %s GL accounts for correspondence, separated by spaces\
              (eg. 50001 50002 50003 etc.).' % type_of_correspondence
            correspondence_accounts = raw_input("> ").split(' ')
            # create new column and mark accounts for which correspondence test will be performed
            data_cleaned['%s correspondence' % type_of_correspondence] = ""
            # launch loop to mark transactions as account or correspondence 
            for account in correspondence_accounts:
                account_transactions = data_cleaned.loc[data_cleaned['Account no'].astype(str) == str(account), 'Transaction ID']
                data_cleaned.loc[data_cleaned['Transaction ID'].isin(account_transactions), '%s correspondence' % type_of_correspondence] = 'Corresponds to %s' % account
                data_cleaned.loc[data_cleaned['Account no'].astype(str) == str(account), '%s correspondence' % type_of_correspondence] = "%s" % type_of_correspondence
                correspondence = data_cleaned.loc[data_cleaned['%s correspondence' % type_of_correspondence] != ""]
   
        # complete and write to file
        correspondence = data_cleaned.loc[data_cleaned['%s correspondence' % type_of_correspondence] != ""]
        correspondence.to_csv(r'%s correspondence.txt' % type_of_correspondence, sep=';', mode='a')
        print '\n'
        print '*'*80
        print "\n%s correspondence test completed in %s correspondence.txt." % (type_of_correspondence, type_of_correspondence)
        




# doesn't really work
"""     data_cleaned.loc[data_cleaned['Account no'].isin(correspondence_accounts), \
      ['%s correspondence' % type_of_correspondence]] = '%s account' % type_of_correspondence
    correspondence_vouchers = data_cleaned.loc[data_cleaned['Account no'].isin(correspondence_accounts),\
      ['Transaction ID']]
      # testing
    for voucher in correspondence_vouchers['Transaction ID'].unique():
        print voucher
        data_cleaned.loc[data_cleaned['Transaction ID'] == voucher].loc[data_cleaned['%s correspondence'\
         % type_of_correspondence] == "", ['%s correspondence' % type_of_correspondence]] = 'Correspondence'\

    correspondence = data_cleaned.loc[data_cleaned['%s correspondence' % type_of_correspondence] != ""]
    correspondence.to_csv(r'%s correspondence.txt' % type_of_correspondence, sep=';', mode='a')
    print '\n'
    print '*'*80
    print "\n%s correspondence test completed in %s correspondence.txt." % (type_of_correspondence, type_of_correspondence) """

data_cleaned, single_column_amount = data_cleaning(data)

correspondence(data_cleaned, single_column_amount)