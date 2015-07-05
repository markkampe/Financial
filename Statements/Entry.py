class Entry:
    """
        A single ledger entry
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
        s = self.date + sep + str(self.amount) + sep
        s += "" if self.account is None else self.account
        s += sep + '"' + self.description + '"'
        return s
