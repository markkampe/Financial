#!/bin/bash
#   starting with (all accounts) Fidelity portfolio download
#   run the interest-paying instrument analyzer on the income account
#   for each element of the ladder:
#	year, quarter, rate, amount, symbol

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
echo -e "year\tqtr\trate\tamount\tsymbol"
echo -e "---\t---\t-----\t------\t------"
grep -v "MMKT" $TEMPFILE | sed 's/\s\s*/ /g' | sed \
	-e 's/0[123]\/[0-9][0-9]\//1 /' \
	-e 's/0[456]\/[0-9][0-9]\//2 /' \
	-e 's/0[789]\/[0-9][0-9]\//3 /' \
	-e 's/1[012]\/[0-9][0-9]\//4 /' | \
    awk '{printf "%s\t%s\t%s\t$%s\t%s\n", $7, $6, $5, $4, $9 }' | \
    sort -k 2,1

rm $TEMPFILE
exit
