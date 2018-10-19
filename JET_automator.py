# coding: utf-8
# copyright Arunas Umbrasas, 2018
# arunas.umb@gmail.com

import pandas as pd
import re
from sys import argv

print '\n'
print '*'*80

# check argv arguments provided, load config if provided, otherwise ask to specify separator
if len(argv) == 3:
    script, filename, i = argv
    # import separator from config file if available
    print '\nImporting %r.' % filename
    with open('config.txt', 'rU') as in_file:
        config_list = in_file.read().split('\n')
    separator = config_list[0]
elif len(argv) == 2:
    script, filename = argv
    # specify separator if config file unavailable
    print '\nImporting %r. Plese specify column separator and press enter. Example what to type: ,' % filename
    separator = raw_input("> ")
    # print help section if help argument is specified
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
data = pd.DataFrame.from_csv(filename, sep=separator, index_col=None)

print 'Import succesful. Following columns imported:\n'
print data.columns
print '\n'
print '*'*80
print '\nSample data:'
print data.head()
print '\n'

# if config is specified, import config settings; otherwise ask for column names to be specified
def data_cleaning(data):
    if len(argv) == 3:
        with open('config.txt', 'rU') as in_file:
            config_list = in_file.read().split('\n')
        print '\nColumn names loaded from config file.'
        print config_list
        # assigning variables from config
        acc_no = config_list[1]
        debit = config_list[2]
        credit = config_list[3]
        trans_ID = config_list[4]
        user_ID = config_list[5]
        trans_date = config_list[6]
        entry_date = config_list[7]
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
        print "Please specify name of the column containing transaction date."
        trans_date = raw_input('> ')
        print "Please specify name of the column containing entry (posting) date."
        entry_date = raw_input('> ')
        # writing column information to file
        config_list = [separator, acc_no, debit, credit, trans_ID, user_ID, trans_date, entry_date]
        with open('config.txt', 'w') as out_file:
            out_file.write('\n'.join(config_list))

    # data cleaning to rename columns and remove currency symbols
    print "\nReconfiguring columns for analysis.\n"
    # test if amounts are in single column or not
    single_column_amount = False
    if debit == credit:
        single_column_amount = True
        data_cleaned = data.rename(columns={acc_no:'Account no', debit: 'Amount',\
            trans_ID: 'Transaction ID', user_ID: 'User ID',\
            trans_date:'Transaction date', entry_date:'Entry date'})
        data_cleaned['Amount'] = data_cleaned.Amount.replace('[\$,)]', '', regex=True)
        data_cleaned['Amount'] = data_cleaned.Amount.replace('[\€,)]', '', regex=True)
        data_cleaned['Amount'] = data_cleaned.Amount.replace('[\EUR,)]', '', regex=True).astype(float)
    else:
        data_cleaned = data.rename(columns={acc_no:'Account no', credit: 'Credit',\
            debit: 'Debit', trans_ID: 'Transaction ID', user_ID: 'User ID',\
            trans_date:'Transaction date', entry_date:'Entry date'})
        data_cleaned['Credit'] = data_cleaned.Credit.replace('[\$,)]', '', regex=True)
        data_cleaned['Debit'] = data_cleaned.Debit.replace('[\$,)]', '', regex=True)
        data_cleaned['Credit'] = data_cleaned.Credit.replace('[\€,)]', '', regex=True)
        data_cleaned['Debit'] = data_cleaned.Debit.replace('[\€,)]', '', regex=True)
        data_cleaned['Credit'] = data_cleaned.Credit.replace('[\EUR,)]', '', regex=True).astype(float)
        data_cleaned['Debit'] = data_cleaned.Debit.replace('[\EUR,)]', '', regex=True).astype(float)
    
    # type conversions that do not depend on single_column_amount
    data_cleaned[['Account no', 'Transaction ID', 'User ID']] = data_cleaned[['Account no', \
    'Transaction ID', 'User ID']].astype(str)
        # type conversions that do not depend on single_column_amount
    date_conversion_fail = True
    try:
        data_cleaned[['Transaction date', 'Entry date']] = data_cleaned[['Transaction date', 'Entry date']].astype('datetime64[ns]')
        date_conversion_fail = False
    except:
        print "[!] Could not convert Transaction date and Entry date columns to dates.\n"
    # complete and print columns, data types
    print '*'*80
    print '\nData cleaning completed. Columns identified as follows:\n'
    print data_cleaned.columns
    print '\n'
    print data_cleaned.dtypes
    return (data_cleaned, single_column_amount, date_conversion_fail)

# completeness test: group by account name and show sum of CR/DR
def completeness_test(data_cleaned, single_column_amount, separator):
    if single_column_amount == True:
        completeness = data_cleaned.groupby(['Account no']).agg({'Amount':'sum'})
    else:
        completeness = data_cleaned.groupby(['Account no']).agg({'Credit':'sum','Debit':'sum'})

    # write to file and complete
    completeness.to_csv(r'completeness.txt', sep=separator, mode='a')
    print '\n'
    print '*'*80
    print "\nCompleteness test completed in completeness.txt."

# cr/dr test: sum all credits and debits
def cr_dr_test(data_cleaned, single_column_amount, separator):
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
    cr_dr.to_csv(r'cr_dr.txt', sep=separator, mode='a')
    print '\n'
    print '*'*80
    print "\nCredits = Debits test completed in cr_dr.txt. Test %s with diff %d." % (result, diff)

# function that writes specified GL account detail to file
def detail(data_cleaned, separator):
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
            detail.to_csv(r'%s detail.txt' % account_detail, sep=separator, mode='a')
            print '\n'
            print '*'*80
            print "\n%s detail saved in %s detail.txt.\n" % (account_detail, account_detail)  

def correspondence(data_cleaned, single_column_amount, separator):
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
            
            # filter out any rows not part of correspondence
            correspondence = data_cleaned.loc[data_cleaned['%s correspondence' % type_of_correspondence] != ""]
            
            # correspondence summary
            if single_column_amount == False:
                correspondence_summary = correspondence.groupby(['Account no', '%s correspondence' % type_of_correspondence]).agg({'Credit': 'sum', 'Debit': 'sum'})
            else:
                correspondence_summary = correspondence.groupby(['Account no', '%s correspondence' % type_of_correspondence]).agg({'Amount': 'sum'})

            # complete and write to file
            correspondence.to_csv(r'%s correspondence.txt' % type_of_correspondence, sep=separator, mode='a')
            correspondence_summary.to_csv(r'%s correspondence summary.txt' % type_of_correspondence, sep=separator, mode='a')
            print '\n'
            print '*'*80
            print "\n%s correspondence test completed in %s correspondence.txt and %s correspondence summary.txt.\n" % (type_of_correspondence, type_of_correspondence, type_of_correspondence)

def user_summary(data_cleaned, single_column_amount, separator):
    if single_column_amount == True:
        user_summary = data_cleaned.groupby(['User ID'])\
        .agg({'Account no': 'count', 'Amount': 'sum'})\
        .rename(columns={'Account no': 'Transaction count'})
    elif single_column_amount == False:
        user_summary = data_cleaned.groupby(['User ID'])\
        .agg({'Account no': 'count', 'Credit': 'sum', 'Debit': 'sum'})\
        .rename(columns={'Account no': 'Transaction count'})
    
    # complete and write to file
    user_summary = user_summary.sort_values(['Transaction count'])
    user_summary.to_csv('user summary.txt', sep=separator, mode='a')
    print '\n'
    print '*'*80
    print "User summary saved in user summary.txt.\n"

def seldom_used(data_cleaned, single_column_amount, separator):
    if single_column_amount == True:
        seldom_summary = data_cleaned.groupby(['Account no'])\
        .agg({'Transaction ID': 'count', 'Amount': 'sum'})\
        .rename(columns={'Transaction ID': 'Transaction count'})
    elif single_column_amount == False:
        seldom_summary = data_cleaned.groupby(['Account no'])\
        .agg({'Transaction ID': 'count', 'Credit': 'sum', 'Debit': 'sum'})\
        .rename(columns={'Transaction ID': 'Transaction count'})
    
    # complete and write to file
    seldom_summary = seldom_summary.sort_values(['Transaction count'])
    seldom_summary.to_csv('seldom used.txt', sep=separator, mode='a')
    print '\n'
    print '*'*80
    print "Seldom used accounts summary saved in seldom used.txt.\n"

def backdated_entries(data_cleaned, separator, date_conversion_fail):
    if date_conversion_fail == True:
        print '\n'
        print '*'*80
        print "[!] Cannot perform test as date conversion failed. Check date format and re-import data file.\n"
        break
    else:
        backdated = data_cleaned.where(data_cleaned['Transaction date'] < data_cleaned['Entry date'])
        backdated.dropna().to_csv('backdated entries.txt', sep=separator, mode='a')
        print '\n'
        print '*'*80
        print "Backdated entries detail saved in backdated entries.txt.\n"

# data cleaning launch
data_cleaned, single_column_amount, date_conversion_fail = data_cleaning(data)

# application menu 
stop_app = False
while stop_app == False:
    print "\n"
    print "*"*80
    print """\nChoose test to perform by typing corresponding number and pressing enter (eg. 1):
    [1] Completeness
    [2] CR=DR
    [3] Correspondence
    [4] User summary
    [5] Seldom used accounts summary
    [6] Back-dated postings (-)
    [7] GL account detail
    [q] Quit application"""
    user_input = raw_input ('> ')
    if user_input == '1':
        completeness_test(data_cleaned, single_column_amount, separator)
    elif user_input == '2':
        cr_dr_test(data_cleaned, single_column_amount, separator)
    elif user_input == '3':
        correspondence(data_cleaned, single_column_amount, separator)
    elif user_input == '4':
        user_summary(data_cleaned, single_column_amount, separator)
    elif user_input == '5':
        seldom_used(data_cleaned, single_column_amount, separator)
    elif user_input == '6':
        backdated_entries(data_cleaned, separator, data_conversion_fail)
    elif user_input == '7':
        detail(data_cleaned, separator)
    elif user_input == 'q':
        stop_app = False
        break
    else:
        print "Input invalid."