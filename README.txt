Accounting

	I have had on-line accounting for over fifty years.  The data has
	always been a very simple set of categories, budgets and ledgers (in
	ASCII text) but the program to operate on them has been rewritten a
	few times (PDP11/UNIX for CURSES, DOS/C, and finally rewritten in Java
	(as a Swing application) when I needed to practice Java before teaching
	a lab.

	An accounts file is a series of account/budget/balance lines, followed
	by indented ledger entries (date, delta, balance, description) under
	each account.  It also includes, at the end (ignored by the program,
	but for my benefit) some simple analytics of per-account performance
	vs budget.
	
	Ledger entries can be entered one at a time, but (more usefully)
	it has the ability to import ledger entries from csv files (date,
	amount, account, description).

Statements

	I played with Mint for a little while, and realized how convenient
	automatic categorization of entries in downloaded statements was.
	So I built a python program to, given csv files, figure out which
	columns are which and then use classification rules to classify
	as many expenses as possible, including some aggregation and
	rewriting.

	Its input is downloaded csv statement records.  Its output is
	(better anotated) csv statements.  It can reprocess its own
	output arbitrarily many times.

FullMonte

	I have generally done my dip-buying "by feel", and did not
	trust myself.  I found 150 years of monthly SP500 data, 
	built a simulator to play random 20y segments against purchase
	simulators, and implemented a few simple purchase strategies.
	It was very useful, in that it showed the futility of waiting 
	a long time for a bigger dip.

	I also found this data to be very useful when the Spring 20
	opportunity came.  I processed the (post 1920) data to find,
	given the market had dropped by X, the probability of it dropping
	by Y more, and then used these to compute what fraction of my
	intended purchases I should make at each 5%. 

FinSim
	
	I created a ludicrously elaborate financial planning spreadsheet.  I
	liked the spreadsheet form because it could easily simultaneously 
	capture old data and forward predictions.  The problem with the
	spreadsheet was that it couldn't handle Monte Carlo variability
	simulations ... which really are very important.

	So I decided to try to construct some building blocks that I could
	use to parametrize growth and then generate simulations within those
	parameters.  It wasn't clear to me whether or not I could make these
	so easily controlled that a non-programmer could use them, but actually
	that wasn't a constraint on my problem.  I haven't worked on them for
	several years now (way too busy) but I want to get back to them because I
	think it might turn out to be a great toolkit for experimenting with
	financial planning.
