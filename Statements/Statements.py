#!/usr/bin/python
#
#   program to process one or more bank statements (in csv format)
#   categorizing entries, optionally aggregating them, and producing
#   standard format columns.
#
#   usage: python Statements.py [options] csv-input-file ...
#
#   options:
#       --rules=file
#
#   input files are in csv format, optional 1st line headers
#
#   Notes:
#       There are two different types of pattern matching done here:
#        1) figuring out what the columns mean
#               preferably based on header lines, but otherwise
#               based on a few hard-coded heuristics
#        2) associating descriptions with accounts
#               which is done by the Rules.Rule class
#               based on rules read in from a configuration file
#
#       In principle we could use a different configuration file
#       per input source ... but (assuming there are no conflicts)
#       it is easier to have a single set of rules that could be
#       applied to reports from multiple institutions.   The primary
#       down-side is that more rules result in slower execution.
#
import sys
from decimal import Decimal
import csv
from Rules import Rules


def findCol(string, array):
    """
        see if any of the columns contains a specified string
    """
    for i in range(len(array)):
        if string in array[i]:
            return i

    return -1


class Entry:
    """
        A single ledger entry
    """

    def __init__(self, date, amount, account, description):
        self.date = date
        self.account = "" if account is None else account
        self.amount = amount
        self.description = description

    def str(self):
        """
            return the canonical string representation
        """
        sep = ", "
        s = self.date + sep + str(self.amount) + sep + self.account + \
            sep + '"' + self.description + '"'
        return s


class Statement:
    """
        Bank statement parser
    """

    def __init__(self, rules):
        """
            constructor for a Statement parser
        """
        self.output = sys.stdout    # default output file
        self.rules = rules          # tranaction clasification rules
        self.process = True         # apply matching rules
        self.sort = False           # sort output by date

        self.tagged = 0             # lines that had acct tags
        self.matched = 0            # lines for which we found acct tags
        self.unmatched = 0          # lines we could not match
        self.file_credit = 0        # per file sum of credits
        self.file_debit = 0         # per file sum of debits
        self.tot_credit = 0         # grand total credits
        self.tot_debit = 0          # grand total debits

        self.aggregations = {}      # accumlating aggregations
        self.buffered = []          # buffered output (for sorting)

    def analyze_headers(self, cols):
        """
            analyze a csv header line to figure out which columns
            contain the fields we care about.

            Args:
                array of column values from the first input line

            Return:
                (bool) could we find all required columns

            Notes:
                The order in which we do these tests is important,
                because a different columns could match different
                rules.

                These titles are hard-coded, but they seem to
                work for a lot of reports.
        """
        if self.date < 0:
            self.date = findCol("Post Date", cols)
        if self.date < 0:
            self.date = findCol("Date", cols)
        if self.date < 0:
            self.date = findCol("date", cols)

        if self.amt < 0 or self.amt == self.date:
            self.amt = findCol("Amount", cols)
        if self.amt < 0 or self.amt == self.date:
            self.amt = findCol("amount", cols)

        if self.desc < 0 or self.desc == self.date or self.desc == self.amt:
            self.desc = findCol("Descr", cols)
        if self.desc < 0 or self.desc == self.date or self.desc == self.amt:
            self.desc = findCol("descr", cols)

        if self.acct < 0 or self.acct == self.date or self.acct == self.amt \
           or self.acct == self.desc:
            self.acct = findCol("Account", cols)
        if self.acct < 0 or self.acct == self.date or self.acct == self.amt \
           or self.acct == self.desc:
            self.acct = findCol("account", cols)

        # see if we found all the critical fields
        return self.date >= 0 and self.amt >= 0 and self.desc >= 0

    def find_date(self, cols):
        """
            find the first column that looks like a date
            (for files that don't begin with a column header line)

            Args:
                array of column values from the first input line

            Return:
                (bool) did we find a date column

            Note:
                Rather than do a proper regexp, I cheat and just
                count characters of different classes.
        """

        # go through the columns one at a time
        for i in range(len(cols)):
            s = cols[i]
            digits = 0
            slashes = 0
            bogus = 0
            # look at every character in this string
            for c in s:
                if c.isdigit():
                    digits += 1
                elif c == "/":
                    slashes += 1
                elif not c.isspace():
                    bogus += 1

            # see if this could plausibly be a date
            if bogus > 0 or slashes < 1 or slashes > 2:
                continue
            if digits < 2 or digits > 8:
                continue
            self.date = i
            return True

        return False

    def find_amt(self, cols):
        """
            find the first column that looks like an amount
            (for files that don't begin with a column header line)

            Args:
                array of column values from the first input line

            Return:
                (bool) did we find an amount column

            Note:
                Rather than do a proper regexp, I cheat and just
                count characters of different classes.
        """

        # go through the columns one at a time
        for i in range(len(cols)):
            # don't reuse columns already discovered
            if i == self.date:
                continue

            s = cols[i]
            digits = 0
            signs = 0
            bogus = 0
            # look at every character in this string
            for c in s:
                if c.isdigit():
                    digits += 1
                elif c == "-" or c == "$" or c == '.':
                    signs += 1
                elif not c.isspace():
                    bogus += 1

            # see if this could plausibly be an amount
            if digits > 0 and signs < 3 and bogus == 0:
                self.amt = i
                return True

        return False

    def find_desc(self, cols):
        """
            find the first column that looks like a description
            (for files that don't begin with a column header line)

            Args:
                array of column values from the first input line

            Return:
                (bool) did we find a description column

            Note:
                Rather than do a proper regexp, I cheat and just
                count characters of different classes.
        """

        # go through the columns one at a time
        for i in range(len(cols)):
            # don't reuse columns already discovered
            if i == self.date or i == self.amt:
                continue

            # heuristic: descriptions are usually quoted
            s = cols[i]
            if s.startswith('"') or s.startswith("'"):
                if "Reference" in s:    # known exception
                    continue
                self.desc = i
                return True
        return True

    def analyze_data(self, cols):
        """
            analyze a header line to figure out what is in each column
            (for files that don't begin with a column header line)

            Args:
                array of column values from the first input line

            Return:
                could we find all required columns

            Note:
                if account names have been added to the file, it will
                have a header line, and we will not have to infer them
        """
        if self.date < 0 and not self.find_date(cols):
            sys.stderr.write("ERROR: unable to identify date column\n")
        if self.amt < 0 and not self.find_amt(cols):
            sys.stderr.write("ERROR: unable to identify amt column\n")
        if self.desc < 0 and not self.find_desc(cols):
            sys.stderr.write("ERROR: unable to identify desc column\n")
        return self.date >= 0 and self.amt >= 0 and self.desc >= 0

    def preamble(self):
        """
            print out the file preamble (column headings)
        """
        self.output.write("Date, Amount, Account, Description" + "\n")

    def process_line(self, cols):
        """
            process a line and either produce standard output or
            accumulate a subtotal to be printed at the end of the
            report
        """
        sep = ", "
        date = cols[self.date]
        amount = Decimal(cols[self.amt])
        desc = cols[self.desc]      # NOTE: this has been unquoted

        # talley credits and debits
        if amount > 0:
            self.file_credit += amount
        else:
            self.file_debit += amount

        # now figure out the account
        entry = None

        # maybe we already have a tag for this line
        if self.acct > 0 and cols[self.acct] != "":
            self.tagged += 1
            acct = cols[self.acct]
        elif self.rules is not None:
            # may be we can use the rules to infer the account
            (acct, aggregate, newdesc) = self.rules.match(desc)
        else:
            acct = None

        # figure out what to do with this entry
        if acct is None:
            self.unmatched += 1
            entry = Entry(date, amount, acct, desc)
        else:
            # NOTE: newdesc has already been quoted
            self.matched += 1
            if aggregate:
                key = acct + "." + newdesc
                if key in self.aggregations:
                    entry = self.aggregations[key]
                    entry.amount += amount
                else:
                    entry = Entry(date, amount, acct, newdesc)
                self.aggregations[key] = entry
                return
            else:
                entry = Entry(date, amount, acct, newdesc)

        # see if we need to accumulate output for sorting
        if (self.sort):
            self.buffered.append(entry)
        else:
            self.output.write(entry.str() + "\n")

    def postscript(self):
        """
            print out the aggregated results and statistics
        """
        # output any items buffered for sorting
        for entry in sorted(self.buffered, key=lambda e: e.date):
            self.output.write(entry.str() + "\n")

        # output aggregated sums (date sorting is meaningless)
        for key in self.aggregations:
            entry = self.aggregations[key]
            self.output.write(entry.str() + "\n")

    def processFile(self, filename):
        """
            process a file

            Note: we use the csv reader rather than split because
                the csv reader knows how to deal with leading/trailing
                white space and delimiters in quoted strings.
        """

        # reinitialize the per-file parameters/statistics
        self.date = -1          # haven't figured out the columns yet
        self.amt = -1           # haven't figured out the columns yet
        self.acct = -1          # haven't figured out the columns yet
        self.desc = -1          # haven't figured out the columns yet
        self.file_credit = 0    # haven't accumulated any data
        self.file_debit = 0     # haven't accumulated any data

        # use the first line to figure out the data format
        input = open(filename, 'rb')
        line = input.readline()
        cols = line.split(',')
        if not self.analyze_headers(cols):
            if not self.analyze_data(cols):
                sys.stderr.write("ERROR: column analysis failed for ")
                sys.stderr.write(filename)
                sys.stderr.write("\n")
                return
            else:
                input.seek(0)       # rewind so we can process it

        # then process the data lines in the file
        reader = csv.reader(input, skipinitialspace=True)
        for cols in reader:
            if len(cols) < 3:       # ignore blank/short lines
                continue
            # make sure we strip all leading/trailing white space
            for c in range(len(cols)):
                cols[c] = cols[c].strip()
            self.process_line(cols)
        input.close()

    def filestats(self, filename):
        """
            output the per file statistics
        """
        statsmsg = "FILE: " + filename
        statsmsg += ",\tcredits=" + str(self.file_credit)
        statsmsg += ",\tdebits=" + str(self.file_debit)
        statsmsg += ",\tnet=" + str(self.file_credit + self.file_debit)
        statsmsg += '\n'
        sys.stderr.write(statsmsg)

        self.tot_credit += self.file_credit
        self.tot_debit += self.file_debit

    def totstats(self):
        """
            output the grand total statistics
        """
        statsmsg = "TOTALS:"
        statsmsg += ",\tcredits=" + str(self.tot_credit)
        statsmsg += ",\tdebits=" + str(self.tot_debit)
        statsmsg += ",\tnet=" + str(self.tot_credit + s.tot_debit)
        statsmsg += '\n'
        sys.stderr.write(statsmsg)

        # output the statistics
        statsmsg = "STATISTICS: "
        statsmsg += "tagged="
        statsmsg += str(self.tagged)
        statsmsg += "\tmatched="
        statsmsg += str(self.matched)
        statsmsg += "\tunmatched="
        statsmsg += str(self.unmatched)
        statsmsg += "\n"
        sys.stderr.write(statsmsg)


if __name__ == '__main__':
    """
        CLI entry point
            process command line arguments
            process the input file(s)
            flush out any accumulated subtotals
    """

    from optparse import OptionParser

    # process the command line arguments
    umsg = "usage: %prog [options] input_file ..."
    parser = OptionParser(usage=umsg)
    parser.add_option("-r", "--rules", type="string", dest="rule_file",
                      metavar="FILE",
                      help="categorizing rules")
    parser.add_option("-o", "--outfile", type="string", dest="out_file",
                      metavar="FILE", default=None,
                      help="output file")
    parser.add_option("-s", "--sort", action="store_true",
                      dest="sort",
                      help="sort output by date")
    parser.add_option("-n", "--nomatch", action="store_true",
                      dest="nomatch",
                      help="suppress rule/account matching")
    (opts, files) = parser.parse_args()

    # digest the categorizing rules
    r = None if opts.nomatch else Rules(opts.rule_file)

    # instantiate a statement object
    s = Statement(r)

    # set the output file
    if opts.out_file is not None:
        s.output = open(opts.out_file, "w")

    # see if we are supposet to sort our output
    if opts.sort:
        s.sort = True

    # process the input files
    if len(files) >= 1:
        # write out a standard file header
        s.preamble()

        # process each input file
        for f in files:
            s.processFile(f)
            s.filestats(f)

        # write out the postscript stuff
        s.postscript()
        s.totstats()
    else:
        sys.stderr.write("ERROR: no input file(s) specified\n")

    if opts.out_file is not None:
        s.output.close()
