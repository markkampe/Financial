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
rules to categorize the entries, and accumulating per-category 
sub-totals.  Realizing that the rules wouldn't catch everything,
I designed it with progressive reprocessing in mind ... you can
run stuff through the program many times, adding rules or annotations
to handle entries not correctly recongized by rules in previous passes.

Basic elements of the solution:
   1. input and output formats are csv
   2. automatic characterization (by header or analysis) of columns
   3. external set of rules to recognize entries
   4. entries can be aggregated or passed through (with attribution)

