#!/usr/bin/python3
import sys
import csv

# lengths of the desired output fields
lAcct = 24
lSym = 12
lValue = 12     # enough for $9999999.99

basis = False       # print basis as well as values
headers = False     # print a line of column headers


def findCol(row, title):
    """ find the row containing a desired heading """
    for x in range(len(row)):
        if row[x] == title:
            return x

    sys.stderr.write("Unable to find column for " + title + "\n")
    sys.exit(-1)


def simplify(file):
    """
    read named (csv) file from a FIDO positions download,
    and print out a simpler version with:
        merely the account, symbol, value (and optional basis)
    """
    # process each line in the CSV file
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        # print out the desired fields from each line
        lineNum = 0
        for row in csv_reader:
            lineNum += 1
            # skip the heading line
            if lineNum == 1:
                xAcct = findCol(row, "Account Name")
                xSym = findCol(row, "Symbol")
                xValue = findCol(row, "Current Value")
                if basis:
                    xBasis = findCol(row, "Cost Basis Total")

                if headers:
                    line = "Account".ljust(lAcct, " ")
                    line += "Symbol".ljust(lSym, " ")
                    line += "Value".rjust(lValue, " ")
                    if basis:
                        line += "Basis".rjust(lValue, " ")
                    print(line)
                    line = "-------".ljust(lAcct, " ")
                    line += "-------".ljust(lSym, " ")
                    line += "----------".rjust(lValue, " ")
                    if basis:
                        line += "----------".rjust(lValue, " ")
                    print(line)
                continue

            # skip lines that don't seem to contain a value
            if len(row) < xValue+1:
                continue
            if not row[xValue]:
                continue

            # extract (and pad) the desired fields
            summary = row[xAcct].ljust(lAcct, " ")
            summary += row[xSym].ljust(lSym, " ")
            summary += row[xValue].rjust(lValue, " ")
            if basis:
                summary += row[xBasis].rjust(lValue, " ")
            print(summary)


def main():

    # parse the arguments
    import argparse
    parser = argparse.ArgumentParser(description='Fidelity Downloads')
    parser.add_argument("filename", nargs='+', help="csv of positions")
    parser.add_argument("--basis",  default=False, action="store_true")
    parser.add_argument("--headers", "-v", default=False, action="store_true")
    args = parser.parse_args()

    if not args.filename:
        sys.stderr.write("Usage: Positions.py [--basis] filename.csv\n")
        sys.exit(-1)
    global basis
    basis = args.basis
    global headers
    headers = args.headers

    # process all of the named files
    for name in args.filename:
        simplify(name)
    sys.exit(0)


if __name__ == "__main__":
    main()
