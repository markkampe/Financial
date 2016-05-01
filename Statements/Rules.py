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
    def __init__(self, pattern, account, descr, process):
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
            rulefile = open(file, 'rb')
            reader = csv.reader(rulefile, skipinitialspace=True)
            for line in reader:
                # ignore blank and comment lines
                if len(line) != 4 or line[0].startswith('#'):
                    continue

                # sanity check all accounts if we have a list
                if accounts and line[1] not in accounts:
                    stderr.write("WARING: unknown account (%s) in rule: %s\n" %
                                 (line[1], line[0]))

                # anything else, we add to the rules list
                self.rules.append(Rule(line[0], line[1], line[2], line[3]))
            rulefile.close()

    def match(self, desc):
        """
            try to find a rule for this description

            Parameters:
                description (unquoted string)

            Returns:
                Entry (with potentially updated account, description)
                should this be confirmed if possible
        """
        # look for a matching rule
        for r in self.rules:
            if fnmatch.fnmatch(desc, r.pat):
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
