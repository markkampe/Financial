#!/usr/bin/python
"""
    program to process one or more bank statements (in csv format)
    categorizing entries, optionally aggregating them, and producing
    standard format columns.

    usage: python Statements.py [options] csv-input-file ...

    options:
        --rules=file

    input files are in csv format, optional 1st line headers

    Notes:
        There are two different types of pattern matching done here:
         1) figuring out what the columns mean
                preferably based on header lines, but otherwise
                based on a few hard-coded heuristics
         2) associating descriptions with accounts
                which is done by the Rules.Rule class
                based on rules read in from a configuration file

        In principle we could use a different configuration file
        per input source ... but (assuming there are no conflicts)
        it is easier to have a single set of rules that could be
        applied to reports from multiple institutions.   The primary
        down-side is that more rules result in slower execution.
"""
import sys
from decimal import Decimal
import csv
# pylint: disable=W0402     # find a new parser
from optparse import OptionParser

from entry import Entry
from rules import Rules
from gui import Gui


def find_col(string, array):
    """
        see if any of the columns contains a specified string
    """
    for index, entry in enumerate(array):
        if string in entry:
            return index

    return -1


class Statement:
    """
        Bank statement parser
    """

    # pylint: disable=R0902     # we have a lot of attributes
    def __init__(self, rules):
        """
        constructor for a Statement parser

        Read in the matching rules, and create an aggregation entry for each
        (account, description) that specifies AGGREGATE processing

        @param rules: (string) name of matching rules file
        """
        self.output = sys.stdout    # default output file
        self.rules = rules          # tranaction clasification rules
        self.process = True         # apply matching rules
        self.sort = False           # sort output by date
        self.interactive = False    # no interactive resolutions

        self.tagged = 0             # lines that had acct tags
        self.matched = 0            # lines for which we found acct tags
        self.unmatched = 0          # lines we could not match
        self.file_credit = 0        # per file sum of credits
        self.file_debit = 0         # per file sum of debits
        self.tot_files = 0          # total files processed
        self.tot_lines = 0          # total lines processed
        self.tot_credit = 0         # grand total credits
        self.tot_debit = 0          # grand total debits

        self.date = -1              # haven't figured out the columns yet
        self.amt = -1               # haven't figured out the columns yet
        self.acct = -1              # haven't figured out the columns yet
        self.desc = -1              # haven't figured out the columns yet
        self.filename = None        # have processed any files
        self.file_line = 0          # haven't processed any lines

        self.buffered = []          # buffered output (for sorting)

        # initialize the aggregations/accounts lists
        self.aggregations = {}      # accumulated values
        self.acc_list = set()       # account menu
        self.agg_list = set()       # aggregation description menu
        date = "99/99/9999"         # will be superceded
        zero = Decimal(0.00)

        # if we have a rule set, us it to populate aggregations/menus
        ruleset = [] if rules is None else rules.rules
        for rule in ruleset:
            self.acc_list.add(rule.acct)
            if rule.process == "AGGREGATE":
                key = rule.acct
                if rule.descr != "":
                    key += "-" + rule.descr
                self.aggregations[key] = Entry(date, zero,
                                               rule.acct, rule.descr)
                self.agg_list.add(rule.descr)
            elif rule.acct not in self.aggregations:
                self.aggregations[rule.acct] = Entry(date, zero, rule.acct, "")

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
            self.date = find_col("Post Date", cols)
        if self.date < 0:
            self.date = find_col("Date", cols)
        if self.date < 0:
            self.date = find_col("date", cols)

        if self.amt < 0 or self.amt == self.date:
            self.amt = find_col("Amount", cols)
        if self.amt < 0 or self.amt == self.date:
            self.amt = find_col("amount", cols)

        if self.desc < 0 or self.desc == self.date or self.desc == self.amt:
            self.desc = find_col("Descr", cols)
        if self.desc < 0 or self.desc == self.date or self.desc == self.amt:
            self.desc = find_col("descr", cols)

        if self.acct < 0 or self.acct == self.date or self.acct == self.amt \
           or self.acct == self.desc:
            self.acct = find_col("Account", cols)
        if self.acct < 0 or self.acct == self.date or self.acct == self.amt \
           or self.acct == self.desc:
            self.acct = find_col("account", cols)

        # see if we found all the critical fields
        return self.date >= 0 and self.amt >= 0 and self.desc >= 0

    def find_date(self, cols):
        """
        find the first column that looks like a date
        (for files that don't begin with a column header line)

        @param cols: [(string)] fields from the first line
        @return: (boolean) did we find a date column
                 and a setting of self.date
        """
        # go through the columns one at a time
        for index, string in enumerate(cols):
            digits = 0
            slashes = 0
            bogus = 0
            # look at every character in this string
            for char in string:
                if char.isdigit():
                    digits += 1
                elif char == "/":
                    slashes += 1
                elif not char.isspace():
                    bogus += 1

            # see if this could plausibly be a date
            if bogus > 0 or slashes < 1 or slashes > 2:
                continue
            if digits < 2 or digits > 8:
                continue
            self.date = index
            return True

        return False

    def find_amt(self, cols):
        """
        find the first column that looks like an amount
        (for files that don't begin with a column header line)

        @param cols: [(string)] fields from the first line

        @return: (boolean) did we find an ammount column
                 and a setting of self.amt
        """
        # go through the columns one at a time
        for index, string in enumerate(cols):
            # don't reuse columns already discovered
            if index == self.date:
                continue

            digits = 0
            signs = 0
            bogus = 0
            # look at every character in this string
            for char in string:
                if char.isdigit():
                    digits += 1
                elif char in ('-', '$', '.'):
                    signs += 1
                elif not char.isspace():
                    bogus += 1

            # see if this could plausibly be an amount
            if digits > 0 and signs < 3 and bogus == 0:
                self.amt = index
                return True

        return False

    def find_desc(self, cols):
        """
        find the first column that looks like a description
        (for files that don't begin with a column header line)

        @param cols: [(string)] fields from the first line

        @return: (boolean) did we find a description column
                 and a setting of self.desc
        """
        # go through the columns one at a time
        for index, string in enumerate(cols):
            if index in (self.date, self.amt):
                continue

            # heuristic: descriptions are usually quoted
            if string.startswith('"') or string.startswith("'"):
                if "Reference" in string:    # known exception
                    continue
                self.desc = index
                return True
        return True

    def analyze_data(self, cols):
        """
        find the first column that looks like a description

        @param cols: [(string)] fields from the first line

        @return: (boolean) did we find all needed columns

        Note: if we are processing our own output, it will have a header line.
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
        accumulate a subtotal to be printed at the end of the report
        """
        # pylint: disable=R0912     # we make a lot of decisions

        # talley credits and debits
        amount = Decimal(cols[self.amt])
        if amount > 0:
            self.file_credit += amount
        else:
            self.file_debit += amount

        # pull out the date, description and (optional) account
        date = cols[self.date]
        desc = cols[self.desc]
        if self.acct > 0 and cols[self.acct] != "":
            self.tagged += 1
            acct = cols[self.acct]
        else:
            acct = None
        entry = Entry(date, amount, acct, desc)

        # see if we use rules to produce account/description
        confirm = False
        if acct is None and self.rules is not None:
            (new_entry, confirm) = self.rules.match(date, desc, amount)
            if new_entry is not None:
                self.matched += 1
                entry.account = new_entry.account
                entry.description = new_entry.description

        #  maybe we can throw up a GUI and ask the user
        if self.interactive and (confirm or entry.account is None):
            gui = Gui(self, entry)
            new_entry = gui.mainloop()
            if new_entry is None:   # delete this entry
                return
            entry.account = new_entry.account
            entry.description = new_entry.description

        if entry.account is None:
            self.unmatched += 1
        else:   # see if this result should be aggregated
            key = entry.account
            if entry.description != "":
                key += "-" + entry.description
            if key in self.aggregations:
                new_entry = self.aggregations[key]
                entry.amount += new_entry.amount
                if new_entry.date < entry.date:
                    entry.date = new_entry.date
                self.aggregations[key] = entry
                return

        # check for commas in the description (scare some parsers)
        if ',' in entry.description:
            sys.stderr.write(f"WARNING: comma in description ({entry.date}:"
                             f" {entry.description}\n")

        # see if we need to accumulate output for sorting
        if self.sort:
            self.buffered.append(entry)
        else:
            self.output.write(entry.str() + "\n")

    def postscript(self):
        """
        print out the aggregated results and statistics

        Note that for "AGGREGATE" rules we do not generate any output until
        we have finished processing all input files.  This method looks
        for the totals we ahve been aggregating and flushes those them out.
        """
        # output any items buffered for sorting
        for entry in sorted(self.buffered, key=lambda e: e.date):
            self.output.write(entry.str() + "\n")

        # output aggregated sums (date sorting is meaningless)
        for key in sorted(self.aggregations):
            entry = self.aggregations[key]
            if entry.amount != 0:
                self.output.write(entry.str() + "\n")

    def process_file(self, filename):
        """
        process a file full of CSV transactions
        - analyze first line to know what is in each column
        - call process_line on each line

        @param file: (string) name of file to be read in
        """

        # reinitialize the per-file parameters/statistics
        self.filename = filename
        self.date = -1          # haven't figured out the columns yet
        self.amt = -1           # haven't figured out the columns yet
        self.acct = -1          # haven't figured out the columns yet
        self.desc = -1          # haven't figured out the columns yet
        self.file_credit = 0    # haven't accumulated any data
        self.file_debit = 0     # haven't accumulated any data
        self.file_line = 0

        # use the first line to figure out the data format
        with open(filename, 'rt', encoding='ascii') as infile:
            line = infile.readline()
            cols = line.split(',')
            if not self.analyze_headers(cols):
                if not self.analyze_data(cols):
                    sys.stderr.write("ERROR: column analysis failed for ")
                    sys.stderr.write(filename)
                    sys.stderr.write("\n")
                    return
                infile.seek(0)       # rewind so we can process it

            # then process the data lines in the file
            reader = csv.reader(infile, skipinitialspace=True)
            for cols in reader:
                self.file_line += 1
                self.tot_lines += 1
                if len(cols) < 3:       # ignore blank/short lines
                    continue
                if cols[0][0] == '#':   # ignore comment lines
                    continue
                # make sure we strip all leading/trailing white space
                for index, string in enumerate(cols):
                    cols[index] = string.strip()
                self.process_line(cols)
            infile.close()
            self.filename = None
            self.tot_files += 1

    def filestats(self, filename):
        """
        output the per file statistics:
        - number of lines procssed
        - total credits, debits, net

        @param filename: (string) name of file just processed

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
        output the grand total statistics for the processed files
        - number of lines procssed
        - total credits, debits, net
        - number of already tagged transactions
        - number of transactions matched by rules
        - number of still un-matched/un-tagged transactions
        """
        statsmsg = "all "
        statsmsg += str(self.tot_files)
        statsmsg += " files, "
        statsmsg += str(self.tot_lines)
        statsmsg += " lines:\t"
        statsmsg += "\tcredits=" + str(self.tot_credit)
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


def read_accounts(file):
    """
    Read in and return a list of known account names

    @param file: (string) name of file to be read in
    @return: [(string)] ... list of account names
    """
    accounts = []
    with open(file, 'rt', encoding='ascii') as afile:
        for line in afile:
            accounts.append(line.strip())
        afile.close()
    return accounts


if __name__ == '__main__':
    # CLI entry point
    # - process command line arguments
    # - for each input file
    #    - process_file
    #    - filestats
    # - totstats

    # process the command line arguments
    parser = OptionParser(usage="usage: %prog [options] input_file ...")
    parser.add_option("-r", "--rules", type="string", dest="rule_file",
                      metavar="FILE", default=None,
                      help="categorizing rules")
    parser.add_option("-a", "--accounts", type="string", dest="acct_file",
                      metavar="FILE", default=None,
                      help="known accounts")
    parser.add_option("-o", "--outfile", type="string", dest="out_file",
                      metavar="FILE", default=None,
                      help="output file")
    parser.add_option("-s", "--sort", action="store_true",
                      dest="sort",
                      help="sort output by date")
    parser.add_option("-i", "--interactive", action="store_true",
                      dest="interactive",
                      help="interactive review/correction")
    (opts, files) = parser.parse_args()

    # digest the list of known accounts
    a = None if opts.acct_file is None else read_accounts(opts.acct_file)

    # digest the categorizing rules
    r = None if opts.rule_file is None else Rules(opts.rule_file, a)

    # instantiate a statement object
    s = Statement(r)

    # set the output file
    # pylint: disable=R1732         # doesn't make sense here
    if opts.out_file is not None:
        s.output = open(opts.out_file, "w", encoding='ascii')

    # check the boolean options
    if opts.sort:
        s.sort = True
    if opts.interactive:
        s.interactive = True

    # process the input
    if len(files) >= 1:
        # write out a standard file header
        s.preamble()

        # process each input file
        for f in files:
            s.process_file(f)
            s.filestats(f)

        # write out the postscript stuff
        s.postscript()
        s.totstats()
    else:
        sys.stderr.write("ERROR: no input file(s) specified\n")

    if opts.out_file is not None:
        s.output.close()
