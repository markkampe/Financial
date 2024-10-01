#!/bin/bash
#   Break the contents of the Retirement Income account into its 
#   (most likely) sub-components: cash, treasuries, CDs and Bonds
#
#   Notes:
#	  this script uses hard-coded column numbers and heuristics
#	  about the identification fields of bonds and CDs ... both
#	  of which could become wrong
#
#	  we don't try to recognize CDs that should be considered
#	  to be short-term (18mo or sooner) cash category.  That
#	  would involve more complex processing than the current
#	  Positions script can do.

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

grep "$account" $input > /tmp/ret_income

echo "$account: Money Market"
total=0.00
grep "MONEY MARKET" /tmp/ret_income | while read line
    do
    	value=`echo $line | cut -d, -f8`	# current value
	echo -e "\t$value"

	# and keep a total
	num=`echo $value | tr -d '$'`
	total=`echo $total + $num | bc`
    done
echo -e "\t---------"
echo -e "\t\$$total"

echo
echo "$account: Treasuries"
total=0.00
grep "S TREAS" /tmp/ret_income | while read line
    do
	what=`echo $line | cut -d, -f4`		# ID sub-field
	when=`echo $what | cut -d' ' -f9`	# maturity date
	face=`echo $line | cut -d, -f5`		# face value
    	value=`echo $line | cut -d, -f8`	# current value
	echo -e "\t$value\t($face $when)"

	# and keep a total
	num=`echo $value | tr -d '$'`
	total=`echo $total + $num | bc`
    done
echo -e "\t---------"
echo -e "\t\$$total"

echo
echo "$account: CDs"
cd_total=0.00
grep " CD " /tmp/ret_income | while read line
    do
	what=`echo $line | cut -d, -f4`		# ID sub-field
	when=`echo $what | cut -d'%' -f2 | cut -d' ' -f2` # maturity date after the rate
	face=`echo $line | cut -d, -f5`		# face value
    	value=`echo $line | cut -d, -f8`	# current value
	echo -e "\t$value\t($face $when)"

	# and keep a total
	num=`echo $value | tr -d '$'`
	cd_total=`echo $cd_total + $num | bc`
    done
echo -e "\t---------"
echo -e "\t\$$cd_total"

echo
echo "$account: others"
oth_total=0.00
grep -v "MONEY MARKET\|S TREAS\| CD " /tmp/ret_income | while read line
    do
	what=`echo $line | cut -d, -f4`		# ID sub-field
	when=`echo $what | cut -d'%' -f2 | cut -d' ' -f2` # maturity date after the rate
	face=`echo $line | cut -d, -f5`		# face value
    	value=`echo $line | cut -d, -f8`	# current value
	echo -e "\t$value\t($face $when)"

	# and keep a total
	num=`echo $value | tr -d '$'`
	oth_total=`echo $oth_total + $num | bc`
    done
echo -e "\t---------"
echo -e "\t\$$oth_total"

total=`echo $cd_total + $oth_total | bc`
echo
echo -e "CDs + others:"
echo -e "\t\$$total"
rm /tmp/ret_income
