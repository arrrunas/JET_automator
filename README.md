# process_automation

JET automator README

Script imports csv file, asks to specify separator and decimal, asks to identify columns for analysis 
and allows to perform the following financial tests automatically:

[1] Completeness
[2] CR=DR
[3] Correspondence
[4] User summary
[5] Seldom used accounts summary
[6] Back-dated postings
[7] General ledger account detail

Test results are saved in .csv files. Output decimal separator is set as ",".

USAGE: 

        JET automator can be launched using one or two arguments as follows:

        python JET automator [data file name] [i] where:

        [data file name] - the name of the datafile, which is contained within the same folder and is .csv
        [i] - flag makes the app import column names from a previous launch (config.txt should be available)
