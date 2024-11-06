"""
    All input and output is in terms lf Ledger Entries
"""


# pylint: disable=R0903     # a purely data class w/several fields
class Entry:
    """
    A single ledger entry (w/date, account, amount, descr)
    """

    def __init__(self, date, amount, account, description):
        self.date = date
        self.account = account
        self.amount = amount
        self.description = description

    def str(self):
        """
            return the canonical string representation
        """
        sep = ", "
        entry = self.date + sep + str(self.amount) + sep
        entry += "" if self.account is None else self.account
        entry += sep + '"' + self.description + '"'
        return entry
