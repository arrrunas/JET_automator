# coding: utf-8
# copyright Arunas Umbrasas, 2018
# arunas.umb@gmail.com

import pandas as pd
import re
from sys import argv

print '\n'
print '*'*80

# filename is specified as script argument, usage: python jet_automator.py filename.csv
if len(argv) == 3:
    script, filename, i = argv
    # import separator from config file if available
    print '\nImporting %r.' % filename
    with open('config.txt', 'rU') as in_file:
        config_list = in_file.read().split('\n')
    separator = config_list[7]
elif len(argv) == 2:
    script, filename = argv
    # specify separator if config file unavailable
    print '\nImporting %r. Plese specify column separator and press enter. Example what to type: ,' % filename
    separator = raw_input("> ")
    if filename == "help":
        print '\n'
        print '*'*80
        print '''\nJET automator help

        USAGE: JET automator can be launched using one or two arguments as follows:

        python JET automator [data file name] [i] where:

        [data file name] - the name of the datafile, which is contained within the same folder and is .csv
        [i] - flag makes the app try to import column names from a previous launch (config.txt should be available)\n'''
        quit()
else:
    print "Please specify at least the data file as argument, eg. python JET_automator.py data.csv or python JET_automator.py help"


# import tasks are run
data = pd.read_csv(filename, error_bad_lines=False, sep=separator)


print 'Import succesful. Following columns imported:\n'
print data.columns
print '\n'
print '*'*80
print '\nSample data:'
print data.head()
print '\n'

# if config is specified, import config settings; otherwise ask for column names to be clarified
def data_cleaning(data):
    if len(argv) == 3:
        with open('config.txt', 'rU') as in_file:
            config_list = in_file.read().split('\n')
        print '\nColumn names loaded from config file.'
        print config_list
        # assigning variables from config
        acc_no = config_list[0]
        debit = config_list[1]
        credit = config_list[2]
        trans_ID = config_list[3]
        user_ID = config_list[4]
        post_date = config_list[5]
        entry_date = config_list[6]
    elif len(argv) == 2:
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
        # writing column information to file
        config_list = [acc_no, debit, credit, trans_ID, user_ID, post_date, entry_date, separator]
        with open('config.txt', 'w') as out_file:
            out_file.write('\n'.join(config_list))

# data cleaning to rename columns and remove currency symbols
    print "\nReconfiguring columns for analysis."
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
    
    # type conversions that do not depend on single_column_amount
    data_cleaned[['Account no', 'Transaction ID', 'User ID']] = data_cleaned[['Account no', \
    'Transaction ID', 'User ID']].astype(str)

    print '\n'
    print '*'*80
    print '\nData cleaning completed. Columns identified as follows:\n'
    print data_cleaned.columns
    print '\n'
    print data_cleaned.dtypes
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

# function that writes specified GL account detail to file
def detail(data_cleaned):
    more_detail = True
    while more_detail == True:
        print '*'*80
        print '\nEnter a GL account for which detail is needed or \'q\' to return to menu.'
        account_detail = raw_input("> ")
        if account_detail == 'q':
            more_detail == False
            break 
        elif str(account_detail) not in data_cleaned['Account no'].tolist():
            print "No such GL account in data.\n"
        else:
            detail = data_cleaned.loc[data_cleaned['Account no'].astype(str) == str(account_detail)]
            # complete and write to file
            detail.to_csv(r'%s detail.txt' % account_detail, sep=';', mode='a')
            print '\n'
            print '*'*80
            print "\n%s detail saved in %s detail.txt.\n" % (account_detail, account_detail)  

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
    
            # complete and write to file
            correspondence = data_cleaned.loc[data_cleaned['%s correspondence' % type_of_correspondence] != ""]
            correspondence.to_csv(r'%s correspondence.txt' % type_of_correspondence, sep=';', mode='a')
            print '\n'
            print '*'*80
            print "\n%s correspondence test completed in %s correspondence.txt.\n" % (type_of_correspondence, type_of_correspondence)

# data cleaning launch
data_cleaned, single_column_amount = data_cleaning(data)

# application menu 
stop_app = False
while stop_app == False:
    print "\n"
    print "*"*80
    print """\nChoose test to perform by typing corresponding number and pressing enter (eg. 1):
    [1] Completeness
    [2] CR=DR
    [3] Correspondence
    [4] User summary (-)
    [5] Seldom used accounts summary (-)
    [6] Back-dated postings (-)
    [7] GL account detail
    [q] Quit application"""
    user_input = raw_input ('> ')
    if user_input == '1':
        completeness_test(data_cleaned, single_column_amount)
    elif user_input == '2':
        cr_dr_test(data_cleaned, single_column_amount)
    elif user_input == '3':
        correspondence(data_cleaned, single_column_amount)
    elif user_input == '7':
        detail(data_cleaned)
    elif user_input == 'q':
        stop_app = False
        break
    else:
        print "Input invalid."