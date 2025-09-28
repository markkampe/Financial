#!/usr/bin/python3
"""
Process a fidelity income statement, identify the interest-paying positions
"""
import sys
import csv
import argparse
from datetime import datetime

# lengths of the desired output fields (including inter-field padding))
L_ACCT = 24
L_TYPE = 12      # CD, US-TREAS, MMKT BOND
L_VALUE = 12     # enough for tens of millions
L_QUANT = 10     # enough for millions
L_RATE = 9       # enough for 99.99%
L_DATE = 14      # mm/dd/yyyy
L_DURATION = 10  # decades
L_SYMBOL = 12    # 8 characters


def find_col(row, title):
    """ find the row containing a desired heading """
    for i, string in enumerate(row):
        if string == title:
            return i

    sys.stderr.write("Unable to find column for " + title + "\n")
    sys.exit(-1)


class Entry():
    """ an instrument description in a maturity-date sorted list """
    # pylint: disable=too-few-public-methods    # this is a data class
    def __init__(self, item_string, date_order):
        self.item = item_string
        self.order = date_order
        self.next = None

    def __str__(self):
        return self.item


# pylint: disable=too-many-locals, too-many-statements, too-many-branches
def simplify(file, entries, headers=False, short_term=0, syms="none"):
    """
    read named (csv) file from a FIDO positions download,
    find the (interest paying) debt instruments
    create and return a date-sorted list of
        account, type, value, amount, rate, date
    """
    now = datetime.now()    # note the current date

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
                x_value = find_col(row, "Current Value")
                x_descr = find_col(row, "Description")
                x_quant = find_col(row, "Quantity")
                x_symbol = find_col(row, "Symbol")

                if headers:
                    line = "Account".ljust(L_ACCT, " ")
                    line += "Type".ljust(L_TYPE, " ")
                    line += "Value".rjust(L_VALUE, " ")
                    line += "Quant".rjust(L_QUANT, " ")
                    line += "Rate".rjust(L_RATE, " ")
                    line += "Date      ".rjust(L_DATE, " ")
                    if short_term > 0:
                        line += "Duration".rjust(L_DURATION, " ")
                    if syms is not None:
                        line += "Symbol".rjust(L_SYMBOL, " ")
                    print(line)

                    line = "-------".ljust(L_ACCT, " ")
                    line += "-------".ljust(L_TYPE, " ")
                    line += "----------".rjust(L_VALUE, " ")
                    line += "------".rjust(L_QUANT, " ")
                    line += "------".rjust(L_RATE, " ")
                    line += "----------".rjust(L_DATE, " ")
                    if short_term > 0:
                        line += "---------".rjust(L_DURATION, " ")
                    if syms is not None:
                        line += "------".rjust(L_SYMBOL, " ")
                    print(line)
                continue

            # skip lines that don't seem to contain a value
            if len(row) < x_value+1:
                continue
            if not row[x_value]:
                continue

            # get and decipher the instrument type
            descr = row[x_descr]
            if 'MONEY MARKET' in descr:
                v_type = "MMKT"
            elif "S TREAS" in descr:
                v_type = "TREAS"
            elif " CD " in descr:
                v_type = "CD"
            else:
                v_type = None

            # see if description includes an interest rate
            if '%' in descr:
                # scan off the rate substring
                pct = descr.index("%")
                pos = pct
                while pos > 0 and descr[pos - 1] != ' ':
                    pos -= 1
                v_rate = descr[pos:pct]
                # limit the precision to .00%
                if '.' in v_rate:
                    dot = v_rate.index(".")
                    if len(v_rate) > dot + 3:
                        v_rate = v_rate[0:dot+3]
                # eliminate leading zero
                if v_rate[0] == '0' and v_rate[1] != '.':
                    v_rate = v_rate[1:]
                v_rate += '%'

                # anything else with a rate, we will call a BOND
                if v_type is None:
                    v_type = "BOND"
            else:
                # probably not a debt instrument
                if v_type is None:
                    continue
                v_rate = ""
                pct = 999

            # see if the rate is followed by a date
            start = pct + 1
            while start < len(descr) and descr[start] == ' ':
                start += 1
            end = start
            while end < len(descr) and descr[end] != ' ':
                end += 1
            if end > start:
                v_date = descr[start:end]
                month = int(v_date[0:2])
                day = int(v_date[3:5])
                year = int(v_date[6:10])
                posn = (365 * year) + (31 * month) + day

                # accumulate this into short vs med/long term income category
                then = datetime(year, month, day)
                distance = (then - now).days
            else:
                v_date = ""
                posn = 0
                distance = 0

            # extract (and pad) the desired fields
            summary = row[x_acct].ljust(L_ACCT, " ")
            summary += v_type.ljust(L_TYPE, " ")
            summary += row[x_value].rjust(L_VALUE, " ")
            summary += row[x_quant].rjust(L_QUANT, " ")
            summary += v_rate.rjust(L_RATE, " ")
            summary += v_date.rjust(L_DATE, " ")

            # figure out if it is short- or long-term
            if short_term > 0 and distance > 0:
                closeness = "near-term" \
                            if distance <= short_term \
                            else "long-term"
                summary += closeness.rjust(L_DURATION, " ")

            # include a (for reference) shortened symbol for bonds
            #   a non-obvious form, but the one I use in Cash Flow sheet
            if syms is not None and v_type != "MMKT":
                v_sym = row[x_symbol]
                if syms == "short":
                    if v_type == "TREAS":
                        v_sym = "US-" + v_sym[6:9]
                    else:
                        v_sym = ".." + v_sym[5:9]
                summary += v_sym.rjust(L_SYMBOL, " ")

            # do a sorted insertion into our list
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

        return entries


def main():
    """
    parse the arguments, process the input files, and print out the report
    """
    # parse the arguments
    parser = argparse.ArgumentParser(description='Fidelity downloads')
    parser.add_argument("file", nargs='+', help="positions csv file")
    parser.add_argument("--headers", "-v", default=False, action="store_true",
                        help="with column headers")
    parser.add_argument("--near", "-n", type=int, dest='near', default=0,
                        help="near term bond duration")
    parser.add_argument("--syms", "-s", type=str, dest='syms',
                        default=None, help="short/long")
    args = parser.parse_args()

    # initialize list of accumulated instruments
    entries = None

    # process all of the named files
    for name in args.file:
        entries = simplify(name, entries=entries,
                           headers=args.headers,
                           short_term=args.near,
                           syms=args.syms)

    # print out the accumulated list of entries
    prev = entries
    while prev is not None:
        print(prev.item)
        prev = prev.next

    sys.exit(0)


if __name__ == "__main__":
    main()
