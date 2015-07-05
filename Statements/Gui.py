from Tkinter import Tk, OptionMenu, Label, LabelFrame, Text, Button, Frame
from Tkinter import StringVar, Entry
from Tkinter import RIDGE, END, TOP, LEFT, BOTH

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
        self.date = entry.date
        self.amount = entry.amount
        self.account = entry.account
        self.description = entry.description

        self.root = Tk()
        self.root.title('Manual Annotation')
        t = Frame(self.root, bd=2 * self.BORDER)

        # top stack: input file name
        f = Frame(t)
        caption = "File: " + statement.filename + ", line: "+ \
            str(statement.file_line)
        Label(f, text=caption).pack()
        f.pack(pady=self.PADDING)

        # middle stack: entry details
        f = Frame(t)
        f1 = LabelFrame(f, text="Date")
        Label(f1, text=self.date).pack(padx=self.PADDING, pady=self.PADDING)
        f1.pack(side=LEFT, padx=self.PADDING)

        f1 = LabelFrame(f, text="Amount")
        Label(f1, text=self.amount).pack(padx=self.PADDING, pady=self.PADDING)
        f1.pack(side=LEFT, padx=self.PADDING)

        f1 = LabelFrame(f, text="Account")
        acct = Text(f1, height=1, width=self.ACCT_WID)
        if entry.account is not None:
            acct.insert(END, self.account)
        acct.pack(padx=self.PADDING, pady=self.PADDING)
        f1.pack(side=LEFT, padx=self.PADDING)

        f1 = LabelFrame(f, text="Description")
        desc = Text(f1, height=1, width=self.DESC_WID)
        desc.insert(END, self.description)
        desc.pack(padx=self.PADDING, pady=self.PADDING)
        f1.pack(side=LEFT, padx=self.PADDING)
        f.pack(pady=self.PADDING)


        # bottom stack: action buttons
        f = Frame(t)
        b = Button(f, text="Accept", command=self.accept)
        b.pack(side=LEFT, padx=self.PADDING)

        self.account = StringVar(f)
        self.account.set(entry.account)
        m = OptionMenu(f, self.account, *sorted(statement.acc_list))
        m.pack(side=LEFT, padx=self.PADDING)
        b = Button(f, text="AGGREGATE")
        b.pack(side=LEFT, padx=self.PADDING)
        b = Button(f, text="Delete",command=self.delete)
        b.pack(side=LEFT, padx=self.PADDING)
        f.pack(padx=self.PADDING, pady=self.PADDING)

        # finalize
        t.pack(side=TOP)

    def accept(self):
        acct = self.account.get()
        if acct == "None":
            acct = None
        self.entry = Entry.Entry(self.date, self.amount, acct,
            self.description)
        self.root.quit()

    def delete(self):
        self.entry = None
        self.root.quit()

    def mainloop(self):
        """
            process the dialog and return the constructed entry
        """
        self.root.mainloop()
        return(self.entry)
