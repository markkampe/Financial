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

account="retirement income"

# so that the total variables survive after the loops are done
shopt -s lastpipe

# generate a report of all of the debt instruments
Income.py $input | grep "$account" > /tmp/ret_income

# left padding for colsum
pad="                    "
line1="                    ----------"
line2="   ------"

# extract the money-market positions
echo "$account: Money Market"
grep "MMKT" /tmp/ret_income | cut -d' ' --complement -f1-2
vtot=`grep "MMKT" /tmp/ret_income | colsum | awk '{print $1}'`
vnum=`grep "MMKT" /tmp/ret_income | colsum | awk '{print $2}'`
echo "$line1"
echo "$pad" $vtot

# extract the CD positions
echo
echo "$account: CDs"
grep "CD" /tmp/ret_income | cut -d' ' --complement -f1-2
vtot=`grep "CD" /tmp/ret_income | colsum | awk '{print $1}'`
vnum=`grep "CD" /tmp/ret_income | colsum | awk '{print $2}'`
echo "$line1" "$line2"
echo "$pad" $vtot "  " $vnum

# extract the treasury positions
echo
echo "$account: Treasuries"
grep "TREAS" /tmp/ret_income | cut -d' ' --complement -f1-2
vtot=`grep "TREAS" /tmp/ret_income | colsum | awk '{print $1}'`
vnum=`grep "TREAS" /tmp/ret_income | colsum | awk '{print $2}'`
echo "$line1" "$line2"
echo "$pad" $vtot "  " $vnum

# extract the bond positions
echo
echo "$account: Other Bonds"
grep "BOND" /tmp/ret_income | cut -d' ' --complement -f1-2
vtot=`grep "BOND" /tmp/ret_income | colsum | awk '{print $1}'`
vnum=`grep "BOND" /tmp/ret_income | colsum | awk '{print $2}'`
echo "$line1" "$line2"
echo "$pad" $vtot "    " $vnum

# sum treasuries + bonds
echo
vnum=`grep -e 'TREAS\|BOND' /tmp/ret_income | colsum | awk '{print $2}'`
echo "TREAS+BOND: " "$pad" $vnum

exit
