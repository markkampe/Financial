import sys
import csv

fieldNames = ["Account Name", "Symbol", "Current Value", "Cost Basis Total"]

# indices of the desired input fields
xAcct = 1
xSym = 2
xValue = 7
xBasis = 99      # I don't want this field

# lengths of the desired output fields
lAcct = 24
lSym = 12
lValue = 12     # $9999999.99
lBasis = 12


def simplify(file):
    """
    read named (csv) file from a FIDO positions download,
    and print out a simpler version with:
        Account Name   Symbol   Current Value   (optional Basis)
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
                # if I were cooler, I would use this to initialize the indices
                continue

            # skip lines that don't seem to contain a position
            if len(row) < xValue+1:
                continue
            if not row[xValue]:
                continue

            # extract (and pad) the desired fields
            summary = row[xAcct].ljust(lAcct, " ")
            summary += row[xSym].ljust(lSym, " ")
            summary += row[xValue].rjust(lValue, " ")
            if len(row) > xBasis:
                summary += row[xBasis].rjust(lBasis, " ")

            print(summary)


def main():
    if len(sys.argv) < 2:
        print("Usage python Positions.py download-file")
    else:
        simplify(sys.argv[1])


if __name__ == "__main__":
    main()
