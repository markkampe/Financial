Accounting

	I have had an on-line check-book for over forty years.  The data has
	always been a very simple set of categories, budgets and ledgers (in
	ASCII text) but the program to operate on them has been rewritten a
	few times (PDP11/UNIX for CURSES, DOS/C, and finally rewritten in Java
	(as a Swing application) when I needed to practice Java before teaching
	a lab.

	Its primary input/output is account/budget/balance lines, followed
	by indented ledger entries (date, delta, balance, description) for 
	each account.  I gradually added more built in analytics, but it is
	basically just a program to enter credits and debits against a bunch
	of accounts.

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
	two years now (way too busy) but I want to get back to them because I
	think it might turn out to be a great toolkit for experimenting with
	financial planning.
