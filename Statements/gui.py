"""
    This is a single-transaction dialog box for characterizing
    entries that could not be definitively classified by rule.
"""
from tkinter import Tk, OptionMenu, Label, LabelFrame, Text, Button, Frame
from tkinter import StringVar
from tkinter import END, TOP, LEFT

from entry import Entry


class Gui():
    """
        Dialog box to confirm/correct an auto-characterization
    """
    # pylint: disable=R0902
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
        main_frame = Frame(self.root, bd=2 * self.BORDER)

        # top stack: input file name
        sub_frame = Frame(main_frame)
        caption = "File: " + statement.filename + ", line: " + \
            str(statement.file_line)
        Label(sub_frame, text=caption).pack()
        sub_frame.pack(pady=self.PADDING)

        # middle stack: entry details
        sub_frame = Frame(main_frame)
        field = LabelFrame(sub_frame, text="Date")
        self.date = Label(field, text=entry.date)
        self.date.pack(padx=self.PADDING, pady=self.PADDING)
        field.pack(side=LEFT, padx=self.PADDING)

        field = LabelFrame(sub_frame, text="Amount")
        self.amount = Label(field, text=entry.amount)
        self.amount.pack(padx=self.PADDING, pady=self.PADDING)
        field.pack(side=LEFT, padx=self.PADDING)

        field = LabelFrame(sub_frame, text="Account")
        self.acct = Text(field, height=1, width=self.ACCT_WID)
        if entry.account is not None:
            self.acct.insert(END, entry.account)
        self.acct.pack(padx=self.PADDING, pady=self.PADDING)
        field.pack(side=LEFT, padx=self.PADDING)

        field = LabelFrame(sub_frame, text="Description")
        self.desc = Text(field, height=1, width=self.DESC_WID)
        self.desc.insert(END, entry.description)
        self.desc.pack(padx=self.PADDING, pady=self.PADDING)
        field.pack(side=LEFT, padx=self.PADDING)
        sub_frame.pack(pady=self.PADDING)

        # bottom stack: action buttons
        sub_frame = Frame(main_frame)
        button = Button(sub_frame, text="Accept", command=self.accept)
        button.pack(side=LEFT, padx=self.PADDING)

        # account selection menu
        self.account = StringVar(sub_frame)
        self.account.set(entry.account)
        menu = OptionMenu(sub_frame, self.account, *sorted(statement.acc_list),
                          command=self.choose_acct)
        menu.pack(side=LEFT, padx=self.PADDING)

        # aggregate description selection menu
        self.description = StringVar(sub_frame)
        self.menu = OptionMenu(sub_frame, self.description,
                               *sorted(statement.agg_list),
                               command=self.choose_desc)
        self.menu.pack(side=LEFT, padx=self.PADDING)

        button = Button(sub_frame, text="Delete", command=self.delete)
        button.pack(side=LEFT, padx=self.PADDING)
        sub_frame.pack(padx=self.PADDING, pady=self.PADDING)

        # finalize
        main_frame.pack(side=TOP)
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
        self.entry = Entry(date, amount, acct, descr)
        self.root.destroy()
        self.root.quit()

    def delete(self):
        """
            Delete button action - return a null Entry
        """
        self.entry = None
        self.root.destroy()
        self.root.quit()

    def choose_acct(self, selection):
        """
            Account menu action - select account
                may have side-effect of enabling standard
                description menu
        """
        self.acct.delete(1.0, END)
        self.acct.insert(1.0, selection)

    def choose_desc(self, selection):
        """
            Description menu action - select a standard description
        """
        # make sure description goes with the account
        acct = self.account.get()
        if acct is not None and self.rules.validFor(selection, acct):
            self.desc.delete(1.0, END)
            self.desc.insert(1.0, selection)

    def mainloop(self):
        """
            process the dialog and return the constructed entry
        """
        self.root.mainloop()
        return self.entry
