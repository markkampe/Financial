#!/usr/bin/python
#
#   This class implements the digesting and execution of rules for
#   mapping ledger descriptions into accounts and comments
#


import csv      # this is much smarter than split(',')
import fnmatch  # use shell wild cards rather than true REs
from sys import stderr
from Entry import Entry


class Rule:
    """
        a rule is:
            a wild-card pattern (not an RE)
            an account name to use (if pattern matches)
            a description to use (if pattern matches)
            how to process the results
                aggregate ... into a category subtotal
                replace ... keep it separate with a new description
                preserve ... keep it separate with original description
                combine ... keep it separate combining new and original
    """
    def __init__(self, date, pattern, account, descr, process):
        self.date = date
        self.pat = pattern
        self.acct = account
        self.descr = descr
        self.process = process


class Rules:
    """
    """
    def __init__(self, filename, accounts=None):
        """
            construct a rule set by reading rules from specified files

            Parameters:
                filename(s) ... string one or more comma separated names

        """
        self.rules = []

        files = filename.split(',')
        for file in files:
            rulefile = open(file, "rt")
            reader = csv.reader(rulefile, skipinitialspace=True)
            for line in reader:
                # ignore blank and comment lines
                if len(line) < 4 or line[0].startswith('#'):
                    continue

                if (len(line) == 4):
                    date = None
                    pat = line[0]
                    acct = line[1]
                    descr = line[2]
                    proc = line[3]
                else:
                    date = line[0]
                    pat = line[1]
                    acct = line[2]
                    descr = line[3]
                    proc = line[4]

                # sanity check all accounts if we have a list
                if accounts and acct not in accounts:
                    stderr.write("WARNING: unknown account (%s) in rule: %s\n"
                                 % (acct, pat))
                    stderr.write("         file: %s, line%s\n" % (file, line))

                # anything else, we add to the rules list
                self.rules.append(Rule(date, pat, acct, descr, proc))
            rulefile.close()

    def match(self, date, desc, amt):
        """
            try to find a rule for this description

            Parameters:
                description (unquoted string)

            Returns:
                Entry (with potentially updated account, description)
                should this be confirmed if possible
        """
        # look for a rule that matches the (date and) description/amount
        s_amt = "%.2f" % (amt)
        for r in self.rules:
            if r.date is not None and date != r.date:
                continue
            combined = str(amt)+"@"+desc
            if (fnmatch.fnmatch(desc, r.pat) or s_amt == r.pat or fnmatch.fnmatch(combined, r.pat)):
                p = r.process
                if p == "AGGREGATE":
                    return (Entry("", 0, r.acct, r.descr), False)
                elif p == "REPLACE":
                    return (Entry("", 0, r.acct, r.descr), False)
                elif p == "COMBINE":
                    newdesc = r.descr + ': ' + desc
                    return (Entry("", 0, r.acct, newdesc), True)
                else:   # preserve
                    return (Entry("", 0, r.acct, desc), False)

        return (None, False)

    def validFor(self, desc, acct):
        """
            is a description part of an account aggregation
        """
        if acct is None:
            return False

        for r in self.rules:
            if r.process != "AGGREGATE":
                continue
            if r.acct != acct:
                continue
            if desc != "" and r.descr != desc:
                continue
            return True

        return False
