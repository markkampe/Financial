#!/bin/bash
#   display the investment (vs income) account positions
#

# figure out what our input file is
if [ -n "$1" ]
then
    input="$1"
else
    input="/home/markk/Downloads/positions.csv"
fi

# filter out the income investments
skip="Retirement-Income"
grep -v $skip $input > /tmp/investments

# print out the remaining cash and equities
./positions.py --headers --basis /tmp/investments

rm /tmp/investments
exit
