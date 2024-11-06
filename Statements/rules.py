#!/usr/bin/python
"""
    This class implements the digesting and execution of rules for
    mapping ledger descriptions into accounts and comments
"""


import csv      # this is much smarter than split(',')
import fnmatch  # use shell wild cards rather than true REs
from sys import stderr
from entry import Entry


# pylint: disable=R0903,R0913         # purely data class
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
    Read a Rule set in from a CSV rules file
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
            with open(file, "rt", encoding='ascii') as rulefile:
                reader = csv.reader(rulefile, skipinitialspace=True)
                for line in reader:
                    # ignore blank and comment lines
                    if len(line) < 4 or line[0].startswith('#'):
                        continue

                    if len(line) == 4:
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
                        stderr.write(f"WARNING: unknown account ({acct})"
                                     f" in rule: {pat}\n")
                        stderr.write(f"         file: {file}, line{line}\n")

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
        s_amt = f"{amt:.2f}"
        for rule in self.rules:
            if rule.date is not None and date != rule.date:
                continue
            combined = str(amt)+"@"+desc
            if (fnmatch.fnmatch(desc, rule.pat) or s_amt == rule.pat
               or fnmatch.fnmatch(combined, rule.pat)):
                proc = rule.process
                if proc == "AGGREGATE":
                    return (Entry("", 0, rule.acct, rule.descr), False)
                if proc == "REPLACE":
                    return (Entry("", 0, rule.acct, rule.descr), False)
                if proc == "COMBINE":
                    newdesc = rule.descr + ': ' + desc
                    return (Entry("", 0, rule.acct, newdesc), True)
                # preserve
                return (Entry("", 0, rule.acct, desc), False)

        return (None, False)

    def valid_for(self, desc, acct):
        """
            is a description part of an account aggregation
        """
        if acct is None:
            return False

        for rule in self.rules:
            if rule.process != "AGGREGATE":
                continue
            if rule.acct != acct:
                continue
            if desc not in ('', rule.descr):
                continue
            return True

        return False
