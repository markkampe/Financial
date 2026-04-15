#!/usr/bin/python3
"""
Process a fidelity income-account statement
    identify the interest-paying positions
    classify them as near-term and long-term
    output information, grouped by type, sorted by maturity
"""
import sys
import csv
import argparse
from datetime import datetime

DAYS_IN_YEAR = 365.0
FAR_FUTURE = 2100       # later than any bond I will own

# lengths of the desired output fields (including inter-field padding))
L_ACCT = 24
L_TYPE = 12      # CD, US-TREAS, MMKT BOND
L_VALUE = 12     # enough for tens of millions
L_QUANT = 10     # enough for millions
L_RATE = 9       # enough for 99.99%
L_DATE = 14      # mm/dd/yyyy
L_DURATION = 10  # decades
L_SYMBOL = 12    # 8 characters

# rates are comuted to the nearest hundredth percent
RATE_DIGITS = 4
RATE_DELTA = 0.0001


def find_col(row, title):
    """ find the row containing a desired heading """
    for i, string in enumerate(row):
        if string == title:
            return i

    sys.stderr.write("Unable to find column for " + title + "\n")
    sys.exit(-1)


class Returns():
    """ aggregate return calculator for a series of investments """
    def __init__(self, title):
        self.title = title  # name of this aggregation
        self.dollars = 0.0  # total dollars in this class
        self.product = 0.0  # sum-product of dollars * rate

    def __str__(self):
        """ generate a report line for this agregate return """
        r = self.product / self.dollars
        s = self.title.ljust(L_TYPE, " ")
        s += f"${self.dollars:.2f}".rjust(L_VALUE, " ")
        s += "".rjust(L_QUANT, " ")
        s += f"{r:.2f}%".rjust(L_RATE, " ")
        return s

    def add(self, amount, rate):
        """ add another instrument to this aggregation """
        self.dollars += amount
        self.product += amount * rate

    def combine(self, other):
        """ combine smaller aggregations into a larger one """
        self.dollars += other.dollars
        self.product += other.product


class Entry():
    """ an instrument description in a maturity-date sorted list """
    entries = None              # list of all analyzed positions

    def __init__(self, item_string, date_order):
        self.item = item_string
        self.order = date_order
        self.next = None

    def __str__(self):
        return self.item

    def append(self):
        """ append a new entry to a list """
        if Entry.entries is None:
            Entry.entries = self
        elif self.order < Entry.entries.order:
            self.next = Entry.entries
            Entry.entries = self
        else:
            prev = Entry.entries
            while prev.next is not None and prev.next.order <= self.order:
                prev = prev.next
            self.next = prev.next
            prev.next = self


def return_rate(future, present, days):
    """ effective rate of return on a discounted zero (within .01%)"""
    # start with a trivially calculated simple interest rate
    increase = (future / present) - 1.0
    years = float(days) / DAYS_IN_YEAR
    annual = round(increase/years, RATE_DIGITS)

    # tweak that until we find the correct compound rate
    while True:     # python does not have do ... until
        # see if a slightly lower rate achieves specified future earnings
        value = present
        period = days
        rate = annual - RATE_DELTA

        # compound interest for specified period
        while period >= DAYS_IN_YEAR:
            value += value * rate
            period -= DAYS_IN_YEAR
        if period > 0:
            value += value * rate * period / DAYS_IN_YEAR

        # if resulting value is too low, previous rate was correct
        if value < future:
            return 100 * rate
        annual = rate


# accumulate aggregate returns each type of debt instrument
cd_returns = Returns("CDs")         # rate of return for CDs
bond_returns = Returns("BONDs")     # rate of return for interest bearing notes
zero_returns = Returns("ZEROes")    # rate of return from OID on zeroes


# pylint: disable=too-many-locals, too-many-statements, too-many-branches
def simplify(file, headers=False, short_term=0, syms="none"):
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
                posn = (DAYS_IN_YEAR * year) + (31 * month) + day

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
                        v_sym = "..." + v_sym[6:9]
                summary += v_sym.rjust(L_SYMBOL, " ")

            # accumulate effective rate for entire portfolio
            s = row[x_value]
            v = float(s[1:]) if s[0] == '$' else float(s)
            if v_rate not in ("", "0.00%"):
                # CDs and bonds with specified rate of return
                r = float(v_rate[:-1])
                if v_type == "CD":
                    cd_returns.add(v, r)
                else:
                    bond_returns.add(v, r)
            elif v_type == 'TREAS' and v_rate == "0.00%":
                # zeroes where we must compute effective return
                a = float(row[x_quant])
                r = return_rate(a, v, distance)
                zero_returns.add(v, r)

            # do a sorted insertion into our list
            entry = Entry(summary, posn)
            entry.append()


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
                        help="near term bond duration (days)")
    parser.add_argument("--syms", "-s", type=str, dest='syms',
                        default=None, help="short/long")
    args = parser.parse_args()

    # process all of the named files
    for name in args.file:
        simplify(name, headers=args.headers,
                 short_term=args.near,
                 syms=args.syms)

    # create additional entries for the aggregate returns
    h = "AGGREGATE-RETURN".ljust(L_ACCT, " ")
    forever = FAR_FUTURE * DAYS_IN_YEAR
    total_returns = Returns("TOTAL")
    for instrument in [cd_returns, bond_returns, zero_returns]:
        if instrument.dollars > 0:
            total_returns.combine(instrument)
            e = Entry(h + str(instrument), forever)
            e.append()

    if total_returns.dollars > 0:
        e = Entry(h + str(total_returns), forever)
        e.append()

    # print out the accumulated list of entries
    prev = Entry.entries
    while prev is not None:
        print(prev.item)
        prev = prev.next

    sys.exit(0)


if __name__ == "__main__":
    main()
