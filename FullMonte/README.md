# MonteCarlo S&P500 Models

## History

I felt that my when-to-buy decisions were being driven by emotions,
and I wanted to base them on data.  I found an archive of S&P 500
data, and implemented a few models to play against it:
   - *all-in* (CDs or market) on day 1
   - buy at the *bottom*
   - *continuous* purchases (e.g. automatic from our pay checks)
   - progressive buying on the *dips*

I started out with a model that could generate months/years of 
either randomly chosen performance or randomly chosen sequences
of a specified length.  If I am going to choose months/years at
random, each needs a growth rate rather than a price.  In retrospect:
   - randomly chosen samples make no sense, because the market
     swings between good and bad times, each of which is 
     likely to have a somewhat standard shape.  Any purchase
     strategy has to work well against those shapes.
  - having a growth rate associated with each month/year,
    even for a chosen sequence of samples, when compounded,
    seemed to result in unreasonable aggregate growth rates.
  - the main reason to use randomly chosen sequences (rather
    than simply enumerating all sequences) is to reduce the
    amount of computation to be performed, which never
    became a problem.
  - the main reason for using annual (vs monthly) samples
    is to reduce the amount of computation to be performed,
    which never became a problem.

So I decided to throw that all away and build a new set of models:
 - based on monthly prices (rather than computed growth rates).
 - based only on real sequences of a specified length
 - that fully explored all sequences of the specified length.

## Infrastructural Modules

### market.py
Digest a .csv of monthly market data, and make a chosen subset of it available
as an array of [$ price, $ dividend, interest-rate] entries.

### compound.py
Functions to compute compound interest or determine the compound interest
rate that would yield an observed result.

### buckets.py
Functions to bucketize an array of data values so we can generate 
probability distribution plots for a reasonable number of points.

## Buying Strategies
All strategies start with $1,000, run for a 20 year period
(experiencing market fluctuations, and receiving interest and dividends)
and report on the final portfolio value at the end of that period.

All strategies are tested over all 20-year sequences between 1970 and 2020.

### strat_all.py
All-In, buy the S&P 500 (or long term Treasuries) at the start of the period.

### strat_bottom.py
Find and buy at the lowest *N* points of the 20 year period.

### strat_continuous.py
Make monthly (automatic investing) purchases over a specified (1-5 year) period.

### strat_dips.py
Watch for the drops, and invest a certain fraction of my money based on how 
much the market has dropped.

### best_worst.py
Report on the range of possible market returns based on fixed holding periods.
(note these returns are for the specified holding period rather than 20 years)

### correction.py
Assess the probability of dips of various sizes, and (based on expectancies)
suggest how much should be invested after dips of a specified size.
