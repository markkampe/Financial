#!/bin/bash
#   Break the contents of the Retirement Income account into its 
#   sub-components: cash, treasuries, CDs and Bonds
#

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
./income.py $input | grep "$account" > /tmp/ret_income

# extract the money-market positions
echo "$account: Money Market"
grep "MMKT" /tmp/ret_income | cut -d' ' --complement -f1 | colsum -v 

# extract the CD positions
echo
echo "$account: CDs"
grep "CD" /tmp/ret_income | cut -d' ' --complement -f1 | colsum -v

# extract the treasury positions
echo
echo "$account: Treasuries"
grep "TREAS" /tmp/ret_income | cut -d' ' --complement -f1 | colsum -v

# extract the bond positions
echo
echo "$account: Other Bonds"
grep "BOND" /tmp/ret_income | cut -d' ' --complement -f1 | colsum -v

echo
echo "$account: TREAS+BOND"
grep "BOND\|TREAS" /tmp/ret_income | cut -d' ' --complement -f1 | colsum

exit
