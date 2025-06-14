#!/bin/bash
#   Break the contents of the Retirement Income account into its 
#   sub-components: cash, treasuries, CDs and Bonds
#
SHORT_TERM=560		# 18 months

# figure out what our input file is
if [ -n "$1" ]
then
    input="$1"
else
    input="/home/markk/Downloads/positions.csv"
fi

account="Retirement-Income"

# so that the total variables survive after the loops are done
shopt -s lastpipe

# generate a report of all of the debt instruments
./income.py --near=$SHORT_TERM $input | grep "$account" > /tmp/ret_income

# extract the money-market positions
echo "$account: Money Market"
grep "MMKT" /tmp/ret_income | cut -d' ' --complement -f1 | colsum -v 

# extract the CD positions
echo
echo "$account: CDs (short term)"
grep "CD" /tmp/ret_income | cut -d' ' --complement -f1 | grep near-term | colsum -v
echo
echo "$account: CDs (long term)"
grep "CD" /tmp/ret_income | cut -d' ' --complement -f1 | grep long-term | colsum -v

# extract the treasury positions
echo
echo "$account: Treasuries"
grep "TREAS" /tmp/ret_income | cut -d' ' --complement -f1 | colsum -v

# extract the bond positions
echo
echo "$account: Other Bonds"
grep "BOND" /tmp/ret_income | cut -d' ' --complement -f1 | colsum -v

echo
echo -n "cash,short term:     "
grep -e "near-term" -e "MMKT" /tmp/ret_income | sed 's/\s\s*/ /g' | cut -d ' ' -f3 | colsum
echo -n "med/long term:       "
grep -e "long-term" /tmp/ret_income | sed 's/\s\s*/ /g' | cut -d ' ' -f3 | colsum
exit
