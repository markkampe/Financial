from Tkinter import Tk, OptionMenu, Label, LabelFrame, Text, Button, Frame
from Tkinter import StringVar, Entry
from Tkinter import END, TOP, LEFT

import Entry


class Gui(object):
    """
        This is a single-transaction dialog box for characterizing
        entries that could not be definitively classified by rule.
    """

    BORDER = 5
    ACCT_WID = 20
    DESC_WID = 40
    PADDING = 5

    def __init__(self, statement, entry):
        """
            instantiate a transaction window
        """
        self.rules = statement.rules

        self.root = Tk()
        self.root.title('Manual Annotation')
        t = Frame(self.root, bd=2 * self.BORDER)

        # top stack: input file name
        f = Frame(t)
        caption = "File: " + statement.filename + ", line: " + \
            str(statement.file_line)
        Label(f, text=caption).pack()
        f.pack(pady=self.PADDING)

        # middle stack: entry details
        f = Frame(t)
        f1 = LabelFrame(f, text="Date")
        self.date = Label(f1, text=entry.date)
        self.date.pack(padx=self.PADDING, pady=self.PADDING)
        f1.pack(side=LEFT, padx=self.PADDING)

        f1 = LabelFrame(f, text="Amount")
        self.amount = Label(f1, text=entry.amount)
        self.amount.pack(padx=self.PADDING, pady=self.PADDING)
        f1.pack(side=LEFT, padx=self.PADDING)

        f1 = LabelFrame(f, text="Account")
        self.acct = Text(f1, height=1, width=self.ACCT_WID)
        if entry.account is not None:
            self.acct.insert(END, entry.account)
        self.acct.pack(padx=self.PADDING, pady=self.PADDING)
        f1.pack(side=LEFT, padx=self.PADDING)

        f1 = LabelFrame(f, text="Description")
        self.desc = Text(f1, height=1, width=self.DESC_WID)
        self.desc.insert(END, entry.description)
        self.desc.pack(padx=self.PADDING, pady=self.PADDING)
        f1.pack(side=LEFT, padx=self.PADDING)
        f.pack(pady=self.PADDING)

        # bottom stack: action buttons
        f = Frame(t)
        b = Button(f, text="Accept", command=self.accept)
        b.pack(side=LEFT, padx=self.PADDING)

        # account selection menu
        self.account = StringVar(f)
        self.account.set(entry.account)
        m = OptionMenu(f, self.account, *sorted(statement.acc_list),
                       command=self.chooseAcct)
        m.pack(side=LEFT, padx=self.PADDING)

        # aggregate description selection menu
        self.description = StringVar(f)
        self.menu = OptionMenu(f, self.description,
                               *sorted(statement.agg_list),
                               command=self.chooseDesc)
        self.menu.pack(side=LEFT, padx=self.PADDING)

        b = Button(f, text="Delete", command=self.delete)
        b.pack(side=LEFT, padx=self.PADDING)
        f.pack(padx=self.PADDING, pady=self.PADDING)

        # finalize
        t.pack(side=TOP)
        self.entry = entry  # default: return what we got

    def accept(self):
        """
            Accept button action - create Entry w/current description
        """
        date = self.date.cget("text")
        amount = self.amount.cget("text")
        acct = self.account.get()
        if acct == "None":
            acct = None
        descr = self.desc.get(1.0, END).replace('\n', '')
        self.entry = Entry.Entry(date, amount, acct, descr)
        self.root.quit()

    def delete(self):
        """
            Delete button action - return a null Entry
        """
        self.entry = None
        self.root.quit()

    def chooseAcct(self, selection):
        """
            Account menu action - select account
                may have side-effect of enabling standard
                description menu
        """
        self.acct.delete(1.0, END)
        self.acct.insert(1.0, selection)
        return

    def chooseDesc(self, selection):
        """
            Description menu action - select a standard description
        """
        # make sure description goes with the account
        acct = self.account.get()
        if acct is not None and self.rules.validFor(selection, acct):
            self.desc.delete(1.0, END)
            self.desc.insert(1.0, selection)
        return

    def mainloop(self):
        """
            process the dialog and return the constructed entry
        """
        self.root.mainloop()
        return(self.entry)
