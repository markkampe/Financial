#!/bin/bash
#   starting with (all accounts) Fidelity portfolio download
#   run the interest-paying instrument analyzer on the income account
#   pull out and separately sub-total the:
#	cash (MMKT) positions
#	short-term CDs
#	med/long-term CDs
#	Treasury notes
#	bonds
#

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

# generate a report of all of the debt instruments
./income.py --near=$SHORT_TERM $input | grep "$ACCOUNT" > $TEMPFILE

# Note: since all of these numbers are coming from a single account, we
#	run a "cut --complement -f1" to simplify the output by removing
#	the (obvious) account name from each line.
#	

# extract the money-market positions
echo
echo "$ACCOUNT: Money Market"
grep "MMKT" $TEMPFILE | cut -d' ' --complement -f1 | colsum -v 

# extract the CD positions
echo
echo "$ACCOUNT: CDs (short term)"
grep "CD" $TEMPFILE | cut -d' ' --complement -f1 | grep $SHORT | colsum -v
echo
# grand total for short-term
echo -n "cash, near-term:     "
grep -e "$SHORT" -e "MMKT" $TEMPFILE | sed 's/\s\s*/ /g' | cut -d ' ' -f3 | colsum

echo
echo "$ACCOUNT: CDs (long term)"
grep "CD" $TEMPFILE | cut -d' ' --complement -f1 | grep $LONG | colsum -v

# extract the treasury positions
echo
echo "$ACCOUNT: Treasuries"
grep "TREAS" $TEMPFILE | cut -d' ' --complement -f1 | colsum -v

# extract the bond positions
echo
echo "$ACCOUNT: Other Bonds"
grep "BOND" $TEMPFILE | cut -d' ' --complement -f1 | colsum -v

# grand total for med/long-term
echo
echo -n "med/long-term:       "
grep -e "$LONG" $TEMPFILE | sed 's/\s\s*/ /g' | cut -d ' ' -f3 | colsum

# second summary for comparison with the Cash Flow Ladder sheet
echo
echo "Bond Ladder Summary:"
grep -v "MMKT" $TEMPFILE | sed 's/\s\s*/ /g' | cut -d ' ' -f4,6 | sed \
	-e 's/0[123]\/[0-9][0-9]\/20/1Q/' \
	-e 's/0[456]\/[0-9][0-9]\/20/2Q/' \
	-e 's/0[789]\/[0-9][0-9]\/20/3Q/' \
	-e 's/1[012]\/[0-9][0-9]\/20/4Q/' | \
    awk '{printf "\t%s %s", $2, $1; if ((NR % 5)==0) { print "" }}'
echo 

rm $TEMPFILE
exit
