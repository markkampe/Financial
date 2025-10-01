#!/bin/bash
# Generate a list of bonds in the income account (cf CashFLow!Ladder)
#
#   starting with (all accounts) Fidelity portfolio download
#       run the interest-paying instrument analyzer on the income account
#       for each element of the ladder:
#	    year, quarter, rate, amount, symbol
#
#   then generate simpler summaries that can (easily) be directly 
#	compared with the bonds in the Ladder page of the Cash Flow sheet.
SHORT_TERM=560			# 18 months (cut-off for short-term income)
TEMPFILE="/tmp/ret_income"	# temp file of income-processed info

DEFAULT="/home/markk/Downloads/positions.csv"

# strings to match in our input
ACCOUNT="Retirement-Income"		# name of income account
SHORT="near-term"			# due before SHORT_TERM
LONG="long-term"			# due after SHORT_TERM

# figure out what our input file is
if [ -n "$1" ]
then
    input="$1"
else
    input="$DEFAULT"
fi
echo "Processing positions download: $input"
echo

# generate a report of all of the debt instruments
./income.py --near=$SHORT_TERM --syms=short $input | grep "$ACCOUNT" > $TEMPFILE

# for each non-MMKT likes from the Income account
#	replace the month with a quarter
#	print the fields in CashFlow!Ladder order
#	print the lines in year,quarter order
echo -e "\tyear  qtr   rate   amount   symbol"
echo -e "\t----  ---  -----  -------   ------"
grep -v "MMKT" $TEMPFILE | sed 's/\s\s*/ /g' | sed \
	-e 's/0[123]\/[0-9][0-9]\//1 /' \
	-e 's/0[456]\/[0-9][0-9]\//2 /' \
	-e 's/0[789]\/[0-9][0-9]\//3 /' \
	-e 's/1[012]\/[0-9][0-9]\//4 /' | \
    awk '{printf "\t%s   %s   %s  $%6s   %s\n", $7, $6, $5, $4, $9 }' | \
    sort -k 2,1

# the next few sets of output are to make it easier to compare the Ladder
#     page of the Cash Flow spread sheet with the Fidelity account statement.

# a simple sum of bond values is a good start
echo
echo "Grand total for ladder size comparison:"
echo -e -n "\t"
grep -v "MMKT" $TEMPFILE | colsum | cut -d' ' -f2


# a list of amounts that can be pasted under the top of the Ladder sheet,
#	and compared with the (already) recorded amounts
echo
echo "Pasteable row of values, for bond-by-bond comparison:"
echo -e -n "\t"
grep -v "MMKT" $TEMPFILE | sed 's/\s\s*/ /g' | sed \
	-e 's/0[123]\/[0-9][0-9]\//1 /' \
	-e 's/0[456]\/[0-9][0-9]\//2 /' \
	-e 's/0[789]\/[0-9][0-9]\//3 /' \
	-e 's/1[012]\/[0-9][0-9]\//4 /' | \
    awk '{printf "%s %s %s,\n", $7, $6, $4 }' | \
    sort -k 2,1 | cut -d' ' -f3 | tr -d '\n'
echo

# a list of symbols that can be pasted under the top of the Ladder sheet,
#	and compared with the (already) recorded symbols.
echo
echo "Pasteable row of symbols, for bond-by-bond comparison:"
echo -e -n "\t"
grep -v "MMKT" $TEMPFILE | sed 's/\s\s*/ /g' | sed \
	-e 's/0[123]\/[0-9][0-9]\//1 /' \
	-e 's/0[456]\/[0-9][0-9]\//2 /' \
	-e 's/0[789]\/[0-9][0-9]\//3 /' \
	-e 's/1[012]\/[0-9][0-9]\//4 /' | \
    awk '{printf "%s %s %6s,\n", $7, $6, $9 }' | \
    sort -k 2,1 | cut -d' ' -f3 | tr -d '\n'
echo


rm $TEMPFILE
exit
