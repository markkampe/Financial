from Tkinter import Tk, OptionMenu, Label, LabelFrame, Text, Button, Frame
from Tkinter import StringVar, Entry
from Tkinter import RIDGE, END, TOP, LEFT, BOTH


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
        self.account = entry.account

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
        Label(f1, text=entry.date).pack(padx=self.PADDING, pady=self.PADDING)
        f1.pack(side=LEFT, padx=self.PADDING)

        f1 = LabelFrame(f, text="Amount")
        Label(f1, text=entry.amount).pack(padx=self.PADDING, pady=self.PADDING)
        f1.pack(side=LEFT, padx=self.PADDING)

        f1 = LabelFrame(f, text="Account")
        acct = Text(f1, height=1, width=self.ACCT_WID)
        acct.insert(END, entry.account)
        acct.pack(padx=self.PADDING, pady=self.PADDING)
        f1.pack(side=LEFT, padx=self.PADDING)

        f1 = LabelFrame(f, text="Description")
        desc = Text(f1, height=1, width=self.DESC_WID)
        desc.insert(END, entry.description)
        desc.pack(padx=self.PADDING, pady=self.PADDING)
        f1.pack(side=LEFT, padx=self.PADDING)
        f.pack(pady=self.PADDING)


        # bottom stack: action buttons
        f = Frame(t)
        Button(f, text="Accept").pack(side=LEFT, padx=self.PADDING)
        Button(f, text="ACCOUUNT").pack(side=LEFT, padx=self.PADDING)
        Button(f, text="AGGREGATE").pack(side=LEFT, padx=self.PADDING)
        Button(f, text="Delete").pack(side=LEFT, padx=self.PADDING)
        f.pack(padx=self.PADDING, pady=self.PADDING)

        # finalize
        t.pack(side=TOP)


    def mainloop(self):
        self.root.mainloop()

        self.account = "***Account***"
        self.aggregate = False
        self.description = "***Description***"
