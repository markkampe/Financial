#!/usr/bin/python3
"""
    Program to process a budgets spreadsheet (CSV download), and create
    a .act (accounting ledger) file for the new year.

    options:
        name of CSV download
        --year=####     ... defaults to current
        --accounts=file    ...
"""
import sys
import csv
import argparse
import datetime


# pylint: disable=too-few-public-methods
class Rule:
    """
    rule defining how an account should be handled
    - account name ... to be used in the ledger
    - account category ... aggregation group in Budget file
    - account item ... sub-item in Budget file

    categories IGNORE and WARN disable the named account,
               either silently (unintersting) or with a
               warning (wrong ledger)

    if item is null, the entier category maps to that account
    """
    def __init__(self, account, category, item):
        self.account = account
        self.category = category
        self.item = item


# pylint: disable=too-few-public-methods
class Rules:
    """ read accounts file to generate a list of accounts """
    def __init__(self, rules_file):
        self.list = []

        got_headers = False
        with open(rules_file, 'rt', encoding='utf-8') as infile:
            reader = csv.reader(infile, skipinitialspace=True)
            for cols in reader:
                # ignoere empty lines
                if len(cols) < 2:
                    continue

                # ignore comments
                if cols[0][0] == '#':
                    continue

                # see if this is the column headers
                if not got_headers:
                    got_headers = True
                    continue

                # pick up the three fields
                acct = cols[0]
                cat = cols[1]
                item = None if len(cols) == 2 else cols[2]

                self.list.append(Rule(acct, cat, item))
            infile.close()


# pylint: disable=too-few-public-methods
class Account:
    """
    one ledger account
    - name of the account
    - monthly budget
    - initial balance
    """
    def __init__(self, name, budget, balance):
        self.name = name
        self.monthly = budget
        self.carry = balance
        self.reported = False


class Accounts:
    """ list of all accounts in ledger """
    def __init__(self, filename, acct_rules):
        """
        process a budget download to generate a list of ledger accounts
        @param name of the Budget csv
        @param list of rules for accounts in this ledger
        """

        # column headings for the detail section
        headings = ['Category', 'Item', 'Monthly']
        self.list = []
        self.rules = acct_rules

        with open(filename, 'rt', encoding='utf-8') as infile:
            reader = csv.reader(infile, skipinitialspace=True)
            processing = False
            for cols in reader:
                # ignore short lines
                if len(cols) < 3:
                    continue

                # ignore lines with no category or budget
                c1 = cols[0]
                c2 = cols[1]
                c3 = cols[2]
                if (c1 == '' or c3 == ''):
                    continue

                # some lines have a balance carried forward
                c4 = cols[3] if len(cols) > 3 else ''

                # ignore lines before the expected column titles
                if processing:
                    self.process(c1, c2, c3, c4)
                elif (c1 == headings[0] and
                      c2 == headings[1] and
                      c3 == headings[2]):
                    processing = True
            infile.close()

    def process(self, cat, item, budget, balance):
        """
        process a Budget csv into a list of ledger accounts

        """

        # see if this one is covered in the rules
        account = None
        # pylint: disable=redefined-outer-name
        for r in self.rules.list:
            # find rules for this category
            if cat != r.category:
                continue
            # see if we have to match the item as well
            if r.item is not None and r.item != item:
                continue
            account = r.account
            break

        # ignore lines which match no rules
        if account is None:
            return
        if account in ['IGNORE', 'WARNING']:
            return

        # turn the dollars and cents into a number
        budget = float(budget.replace('$', '').replace(',', ''))
        if balance == '':
            balance = 0.0
        else:
            balance = float(balance.replace('$', '').replace(',', ''))

        # see if we already have an entry for this account
        # pylint: disable=redefined-outer-name
        for a in self.list:
            if a.name == account:
                a.monthly += budget
                a.carry += balance
                return

        # create a new ledger entry for this account
        self.list.append(Account(account, budget, balance))


if __name__ == '__main__':
    # CLI entry point
    #   process command line arguments
    #   read in the list accounts binding rules
    #   process the provided input file
    #   produce the requested accounts file

    # process the command line arguments
    parser = argparse.ArgumentParser(description='accounting ledger creation')
    parser.add_argument("file", nargs='+',
                        help="Budget sheet CSV")
    parser.add_argument("-a", "--accounts", default="accounts.csv",
                        help="file of category/item->account rules")
    parser.add_argument("-y", "--year", default=None,
                        help="year for new ledger")
    args = parser.parse_args()
    if args.file is None:
        sys.exit(-1)

    # figure out what year we should use
    year = datetime.datetime.today().year if args.year is None else args.year

    # digest the rules for the included accounts
    rules = Rules(args.accounts)

    # process the budget file
    for f in args.file:
        accounts = Accounts(f, rules)

    # generate starting entries for accounts in this ledger, in Rule order
    for r in rules.list:
        if r.category in ['IGNORE', 'WARNING']:
            continue

        # find the entry for this (not yet reported) account
        for a in accounts.list:
            if a.name == r.account:
                if a.reported is False:
                    print(f"ACCOUNT: {a.name:16}", end='    ')
                    print(f"Budget: ${a.monthly:.2f} /mo", end='    ')
                    print(f"Balance: ${a.carry:.2f}")
                    print(f"         0/01/{year}\t${a.carry:.2f}", end='    ')
                    if a.carry == 0:
                        print("initial balance")
                    else:
                        print("Carry forward")
                    print()
                    a.reported = True
                break

    # generate a list of accounts to ignore in this ledger
    for r in rules.list:
        if r.category == 'IGNORE':
            print(f"IGNORE: {r.account}")
        elif r.category == 'WARNING':
            print(f"IGNORE! {r.account}")

    # that's all foslks
    print()
    print("END")
