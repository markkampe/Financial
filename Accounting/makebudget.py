#!/usr/bin/python3
"""
    Program to process a budgets spreadsheet (CSV download), and create
    a .act (accounting ledger) file for the new year.

    options:
        name of CSV download
        --year=####     ... defaults to current
        --accounts=file    ...
        --carry         ... file full of balance carry forwards

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
    """ list of desired accounts and how to handle them """
    def __init__(self, infile):
        del infile              # instead of hard-coded rules below
        self.list = []

        # if I ever need to change these, the right thing to do is create
        #    a new CSV file containing all of this information.

        # categories that translate directly into accounts
        self.list.append(Rule('Basic', 'Basic', None))
        self.list.append(Rule('Medical', 'Medical', None))
        self.list.append(Rule('Utilities', 'Utilities', None))
        self.list.append(Rule('Household', 'Home', None))
        self.list.append(Rule('Transportation', 'Transportation', None))
        self.list.append(Rule('Large-Expenses', 'Amortization', None))
        self.list.append(Rule('JM_ins', 'JM_ins', None))
        self.list.append(Rule('JK_ins', 'JK_ins', None))
        self.list.append(Rule('Reimbursable', 'Reimbursable', None))

        # categories that include multiple accounts
        self.list.append(Rule('Groceries', 'Living', 'groceries'))
        self.list.append(Rule('Clothing', 'Living', 'clothing'))
        self.list.append(Rule('Misc', 'Living', 'postage'))
        self.list.append(Rule('Gifts', 'QoL', 'gifts'))
        self.list.append(Rule('Vacations', 'QoL', 'vacations'))
        self.list.append(Rule('Donations', 'QoL', 'donations'))
        self.list.append(Rule('Food-and-Fun', 'QoL', 'dinner/fun'))
        self.list.append(Rule('Food-and-Fun', 'QoL', 'lunches'))
        self.list.append(Rule('Food-and-Fun', 'QoL', 'alcohol'))
        self.list.append(Rule('Toys', 'QoL', 'toys'))
        self.list.append(Rule('Hobbies', 'QoL', 'hobbies'))
        self.list.append(Rule('Misc', 'QoL', 'subscriptions'))
        self.list.append(Rule('Misc', 'QoL', 'dues'))
        self.list.append(Rule('JM_ins', 'external', 'JM_ins'))
        self.list.append(Rule('JK_ins', 'external', 'JK_ins'))

        # entries that aren't relevant to accounting
        self.list.append(Rule('Cash', "IGNORE", None))
        self.list.append(Rule('Deposit', "IGNORE", None))
        self.list.append(Rule('CreditCard', "IGNORE", None))
        self.list.append(Rule('Transfer', "IGNORE", None))
        self.list.append(Rule('Taxes', "IGNORE", None))
        self.list.append(Rule('Special', "IGNORE", None))

        # entries that go in other ledgers
        self.list.append(Rule('TP-Improve', 'WARNING', None))
        self.list.append(Rule('LA-Improve', 'WARNING', None))
        self.list.append(Rule('SCUBA-mship', 'WARNING', None))
        self.list.append(Rule('SCUBA-ins', 'WARNING', None))
        self.list.append(Rule('SCUBA-matls', 'WARNING', None))
        self.list.append(Rule('SCUBA-gear', 'WARNING', None))
        self.list.append(Rule('SCUBA-maint', 'WARNING', None))
        self.list.append(Rule('SCUBA-expenses', 'WARNING', None))
        self.list.append(Rule('SCUBA-pay', 'WARNING', None))


# pylint: disable=too-few-public-methods
class Account:
    """
    one ledger account
    - name of the account
    - monthly budget
    - current balance
    """
    def __init__(self, name, budget):
        self.name = name
        self.monthly = budget
        self.carry = 0.00
        self.reason = None


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

                # ignore lines before the expected column titles
                if processing:
                    self.process(c1, c2, c3)
                elif (c1 == headings[0] and
                      c2 == headings[1] and
                      c3 == headings[2]):
                    processing = True
            infile.close()

    def process(self, cat, item, budget):
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

        # see if we already have an entry for this account
        # pylint: disable=redefined-outer-name
        for a in self.list:
            if a.name == account:
                a.monthly += budget
                return

        # create a new ledger entry for this account
        self.list.append(Account(account, budget))

    def carry_over(self, filename):
        """ associate a carry over balance with an account """

        with open(filename, 'rt', encoding='utf-8') as infile:
            reader = csv.reader(infile, skipinitialspace=True)
            for cols in reader:
                if len(cols) < 2:
                    continue
                if cols[0][0] == '#':
                    continue
                # pylint: disable=redefined-outer-name
                for a in self.list:
                    if a.name == cols[0]:
                        a.carry = float(cols[1])
                        if len(cols) > 2:
                            a.reason = cols[2]
                        break
            infile.close()


if __name__ == '__main__':
    # CLI entry point
    #   process command line arguments
    #   read in the list of accounts
    #   process the provided input file
    #   produce the requested accounts file

    # process the command line arguments
    parser = argparse.ArgumentParser(description='accounting ledger creation')
    parser.add_argument("file", nargs='+',
                        help="Budget sheet CSV")
    parser.add_argument("-a", "--accounts", default=None,
                        help="file of category/item->account rules")
    parser.add_argument('-c', '--carry', default=None,
                        help="carry-over CSV")
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

    # process any carry-overs
    if args.carry:
        accounts.carry_over(args.carry)

    # generate starting entries for the accounts in this ledgetr
    for a in accounts.list:
        print(f"ACCOUNT: {a.name:16}", end='    ')
        print(f"Budget: ${a.monthly:.2f} /mo", end='    ')
        print(f"Balance: ${a.carry:.2f}")
        print(f"         0/01/{year}\t${a.carry:.2f}", end='    ')
        if a.carry == 0:
            print("initial balance")
        elif a.reason is not None:
            print(f"Carry forward {a.reason}")
        else:
            print("Carry forward")
        print()

    # generate a list of accounts to ignore in this ledger
    for r in rules.list:
        if r.category == 'IGNORE':
            print(f"IGNORE: {r.account}")
        elif r.category == 'WARNING':
            print(f"IGNORE! {r.account}")

    # that's all foslks
    print()
    print("END")
