# MonteCarlo S&P500 Models

## History

I felt that my when-to-buy decisions were being driven by emotions,
and I wanted to base them on data.  I found an archive of S&P 500
data, and implemented a few models to play againat it:

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
as an array of [price, dividend, interest-rate] entried.

### compound.py
Functions to compute compound interest or determine the compound interest
rate that would yield a given result.

### buckets.py
Functions to bucketize an array of data values so we can generate 
probability distributions for a reasonable number of points.

## Buying Strategies
All strategies start with $1,000, run for a 20 year period
(with market fluctuations, and receiving interest and dividends)
and report on the final portfolio value at the end of that period.

### strat_all.py
All-In, buy the market (or a long term CD) at the start of the period.

### strat_bottom.py
Find and buy at the lowest *N* points of the 20 year period.

### strat_continuous.py
Make monthly (automatic investing) purchases over a specified period of time.

### strat_dips.py
Look for the drops, and invest a certain fraction of my money based on how 
much the market has dropped.

### correction.py
Assess the likely returns from a range of buy-on-the-dips parameters.

### best_worst.py
Report on the range of possible market returns as a function of 
holding period.
