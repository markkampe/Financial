#!/usr/bin/python3
"""
Simplify a Fidelity positions download
"""
import sys
import csv
import argparse


# lengths of the desired output fields
L_ACCT = 24
L_SYM = 12
L_VALUE = 12     # enough for $9999999.99


def find_col(row, title):
    """ find the row containing a desired heading """
    for i, string in enumerate(row):
        if string == title:
            return i

    sys.stderr.write("Unable to find column for " + title + "\n")
    sys.exit(-1)


def simplify(file, basis=False, headers=False):
    """
    read named (csv) file from a FIDO positions download,
    and print out a simpler version with:
        merely the account, symbol, value (and optional basis)
    """
    # process each line in the CSV file
    with open(file, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        # print out the desired fields from each line
        line_num = 0
        for row in csv_reader:
            line_num += 1
            # skip the heading line
            if line_num == 1:
                x_acct = find_col(row, "Account Name")
                x_sym = find_col(row, "Symbol")
                x_value = find_col(row, "Current Value")
                if basis:
                    x_basis = find_col(row, "Cost Basis Total")

                if headers:
                    line = "Account".ljust(L_ACCT, " ")
                    line += "Symbol".ljust(L_SYM, " ")
                    line += "Value".rjust(L_VALUE, " ")
                    if basis:
                        line += "Basis".rjust(L_VALUE, " ")
                    print(line)
                    line = "-------".ljust(L_ACCT, " ")
                    line += "-------".ljust(L_SYM, " ")
                    line += "----------".rjust(L_VALUE, " ")
                    if basis:
                        line += "----------".rjust(L_VALUE, " ")
                    print(line)
                continue

            # skip lines that don't seem to contain a value
            if len(row) < x_value+1:
                continue
            if not row[x_value]:
                continue

            # extract (and pad) the desired fields
            summary = row[x_acct].ljust(L_ACCT, " ")
            summary += row[x_sym].ljust(L_SYM, " ")
            summary += row[x_value].rjust(L_VALUE, " ")
            if basis:
                summary += row[x_basis].rjust(L_VALUE, " ")
            print(summary)


def main():
    """
    read the input and print out its simplified form
    """
    # parse the arguments
    parser = argparse.ArgumentParser(description='Fidelity Downloads')
    parser.add_argument("filename", nargs='+', help="csv of positions")
    parser.add_argument("--basis",  default=False, action="store_true")
    parser.add_argument("--headers", "-v", default=False, action="store_true")
    args = parser.parse_args()

    if not args.filename:
        sys.stderr.write("Usage: Positions.py [--basis] filename.csv\n")
        sys.exit(-1)

    # process all of the named files
    for name in args.filename:
        simplify(name, basis=args.basis, headers=args.headers)
    sys.exit(0)


if __name__ == "__main__":
    main()
