Bank Statement Processing
=================
I have spent years going over credit card statements, categorizing expenses,
and accumulating per-category sub-totals.  I looked at mint's ability to
categorize expenses ... but it wanted to impose a lot of other structure 
(and services) on me.  Then I thought about what Mint was doing, and 
realized that it is (now) trivial:
   * banks and credit cards all support csv activity downloads
   * a few dozen regexp rules can easily categorize most expenses
   * computers are great at per-category sub-totals

So I decided to build a simple python application that can process
csv format statements into a standard form, applying pattern matching
rules to categorize the entries, and accumulating per-category sub-totals.

Realizing that the rules wouldn't catch everything, I designed it with
progressive reprocessing in mind ... you can run stuff through the program
many times, adding rules or annotations to handle entries not correctly
recongized by rules in previous passes.

Basic elements of the solution:
   1. input and output formats are csv
   2. automatic characterization (by header or analysis) of columns
   3. external set of rules to recognize entries
      (either by regexp for the description or by date and amount)
   4. entries can be aggregated or passed through (with attribution)

Softare:
	Statements.py	this is the real program
		read in the regexp-to-account matching rules
		for each input file
		    analyze it to figure out the columns
		    process each transaction line 
			find the first matching rule
			adding accounts & descriptions
			if rule is COMBINE, get GUI confirmation
			output the annotated transaction

	Gui.py		a simple GUI for accepting/annotating uncertain matches
	Entry.py	ledger entry with date, account, amount, description
	Rules.py	load and match against a set of regexp-to-account rules

	rules.csv	my (evolving) set of regexp-to-account rules

TEST Data

	I am embarassed to admit that I never created a formal test suite.
	Obviously I should create file of transactions that require different
	types of matching rules ... but the program has worked so well that
	I never felt the need to write a test suite :-)

	I have a few input files that I used once :-)
	  normal.csv	transactions (w/headers) where one requires matching
	  test.csv	the expected output (with correct rule matching)
	  ref.csv	typical first-pass output (after rules got the easy stuff)
