#!/usr/bin/python3
import sys
import csv

# lengths of the desired output fields (including inter-field padding))
lAcct = 24
lType = 12      # CD, US-TREAS, MMKT BOND
lValue = 12     # enough for tens of millions
lQuant = 10     # enough for millions
lRate = 9       # enough for 99.99%
lDate = 14      # mm/dd/yyyy

headers = False     # print a line of column headers


def findCol(row, title):
    """ find the row containing a desired heading """
    for x in range(len(row)):
        if row[x] == title:
            return x

    sys.stderr.write("Unable to find column for " + title + "\n")
    sys.exit(-1)


class Entry(object):

    def __init__(self, item_string, date_order):
        self.item = item_string
        self.order = date_order
        self.next = None

    def __str__(self):
        return self.item


# sorted list of entries to be printed
entries = None


def simplify(file):
    """
    read named (csv) file from a FIDO positions download,
    and print out a simpler version with:
        account, type, value, amount, rate, date
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
                xDescr = findCol(row, "Description")
                xQuant = findCol(row, "Quantity")

                if headers:
                    line = "Account".ljust(lAcct, " ")
                    line += "Type".ljust(lType, " ")
                    line += "Value".rjust(lValue, " ")
                    line += "Quant".rjust(lQuant, " ")
                    line += "Rate".rjust(lRate, " ")
                    line += "Date      ".rjust(lDate, " ")
                    print(line)

                    line = "-------".ljust(lAcct, " ")
                    line += "-------".ljust(lType, " ")
                    line += "----------".rjust(lValue, " ")
                    line += "------".rjust(lQuant, " ")
                    line += "------".rjust(lRate, " ")
                    line += "----------".rjust(lDate, " ")
                    print(line)
                continue

            # skip lines that don't seem to contain a value
            if len(row) < xValue+1:
                continue
            if not row[xValue]:
                continue

            # get and decipher the instrument type
            descr = row[xDescr]
            if 'MONEY MARKET' in descr:
                vType = "MMKT"
            elif "S TREAS" in descr:
                vType = "TREAS"
            elif " CD " in descr:
                vType = "CD"
            else:
                vType = None

            # see if description includes an interest rate
            if '%' in descr:
                # scan off the rate substring
                pct = descr.index("%")
                pos = pct
                while pos > 0 and descr[pos - 1] != ' ':
                    pos -= 1
                vRate = descr[pos:pct]
                # limit the precision to .00%
                if '.' in vRate:
                    dot = vRate.index(".")
                    if len(vRate) > dot + 3:
                        vRate = vRate[0:dot+3]
                # eliminate leading zero
                if vRate[0] == '0' and vRate[1] != '.':
                    vRate = vRate[1:]
                vRate += '%'

                # anything else with a rate, we will call a BOND
                if vType is None:
                    vType = "BOND"
            else:
                # probably not a debt instrument
                if vType is None:
                    continue
                else:
                    vRate = ""
                    pct = 999

            # see if the rate is followed by a date
            start = pct + 1
            while start < len(descr) and descr[start] == ' ':
                start += 1
            end = start
            while end < len(descr) and descr[end] != ' ':
                end += 1
            if end > start:
                vDate = descr[start:end]
                month = int(vDate[0:2])
                day = int(vDate[3:5])
                year = int(vDate[6:10])
                posn = (365 * year) + (31 * month) + day
            else:
                vDate = ""
                posn = 0

            # extract (and pad) the desired fields
            summary = row[xAcct].ljust(lAcct, " ")
            summary += vType.ljust(lType, " ")
            summary += row[xValue].rjust(lValue, " ")
            summary += row[xQuant].rjust(lQuant, " ")
            summary += vRate.rjust(lRate, " ")
            summary += vDate.rjust(lDate, " ")

            # do a sorted insertion into our list
            global entries
            entry = Entry(summary, posn)
            if entries is None:
                entries = entry
            elif entry.order < entries.order:
                entry.next = entries.order
                entries = entry
            else:
                prev = entries
                while prev.next is not None and prev.next.order < entry.order:
                    prev = prev.next
                entry.next = prev.next
                prev.next = entry


def main():

    # parse the arguments
    import argparse
    parser = argparse.ArgumentParser(description='Fidelity Downloads')
    parser.add_argument("filename", nargs='+', help="csv of positions")
    parser.add_argument("--headers", "-v", default=False, action="store_true")
    args = parser.parse_args()

    if not args.filename:
        sys.stderr.write(
            "Usage: Positions.py [--headers] filename.csv\n")
        sys.exit(-1)
    global headers
    headers = args.headers

    # process all of the named files
    for name in args.filename:
        simplify(name)

    # print out the accumulated list of entries
    prev = entries
    while prev is not None:
        print(prev.item)
        prev = prev.next

    sys.exit(0)


if __name__ == "__main__":
    main()
