#!/usr/bin/python
#
#   This class implements the digesting and execution of rules for
#   mapping ledger descriptions into accounts and comments
#


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


import csv      # this is much smarter than split(',')
import fnmatch  # use shell wild cards rather than true REs


class Rules:
    """
    """
    def __init__(self, filename):
        """
            construct a rule set by reading rules from a specified file

        """
        self.rules = []

        rulefile = open(filename, 'rb')
        reader = csv.reader(rulefile, skipinitialspace=True)
        for line in reader:
            # ignore blank and comment lines
            if len(line) != 4 or line[0].startswith('#'):
                continue

            # anything else, we add to the rules list
            self.rules.append(Rule(line[0], line[1], line[2], line[3]))
        rulefile.close()

    def match(self, desc):
        """
            try to find a rule for this description

            Parameters:
                description (unquoted string)

            Returns:
                account name (or None)
                (boolean) should this line be aggregated
                quoted replacement description string
        """
        # look for a matching rule
        for r in self.rules:
            if fnmatch.fnmatch(desc, r.pat):
                p = r.process
                if p == "AGGREGATE":
                    return (r.acct, True, '"' + r.descr + '"')
                elif p == "REPLACE":
                    return (r.acct, False, '"' + r.descr + '"')
                elif p == "COMBINE":
                    newdesc = '"' + r.descr + ': ' + desc + '"'
                    return (r.acct, False, newdesc)
                else:   # preserve
                    return (r.acct, False, '"' + desc + '"')

        return (None, False, '"' + desc + '"')