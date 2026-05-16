#!/usr/bin/python3
"""
Find the best and worst returns for specified investment periods
"""
import sys
import matplotlib.pyplot as plt
from market import Market
from buckets import bucketwidth, bucketize, distribution, value_offset
from compound import compound_rate


# graphical output parameters
OUTPUT = None
TITLE = "Distribution of returns"

# general simulation parameters
FIRST_YEAR = 1950           # first year of market dta
LAST_YEAR = 2020            # last year of market data
MIN_YEARS = 1               # minimum holding period
MAX_YEARS = 20              # masximum holding period


def total_return(sequence, first, years, monthly=False):
    """
        compute the net return for the specified period
        :param sequence: a list of (return, dividend, interest) tupples
        :param first:    the first tupple to be used
        :param years:    the number of tupples to be used
        :param momthly:  is this a monthly sequence
        :returnn (float): value(end)/value(start)
    """
    # apply each year's growh and dividends
    balance = 1.0
    points = years * 12 if monthly else years
    for i in range(points):
        (growth, div, _int) = sequence[first + i]
        if monthly:
            div /= 12
        balance *= (1.0 + growth + div)

    return balance


def main(args):
    """
    for all possible sequences of specified number of years
        compute the aggregate return (gains + dividends)
        tracking the best and worst total returns
    :param (string): name of market data CSV file
    :param -v:   produce verbose output
    :param (int) period: period to be bucketized
    """
    # process the command line arguments
    market_data = "sp500.csv"
    verbose = False
    period = 0
    monthly = True
    for _i, arg in enumerate(args):
        if arg in ('-v', '--verbose'):
            verbose = True
        elif arg.isdigit():
            period = int(arg)
        else:
            market_data = arg

    # get a standard market simulator
    simulator = Market(market_data,
                       start=FIRST_YEAR, end=LAST_YEAR, monthly=monthly)
    sequences = simulator.chosen()

    # find the best and worst return for each investment period
    for years in range(MIN_YEARS, MAX_YEARS+1):
        worst = 666.0
        best = -666.0
        count = 0

        # try all sequences for the current duration
        final = len(sequences) - (12 * years)
        for i in range(final):
            ret = total_return(sequences, i, years)
            if ret < worst:
                worst = ret
            if ret > best:
                best = ret
            count += 1

        if verbose:
            print(f"{years:2d} years, {count} sequences:" +
                  f"{worst:5.1f} - {best:5.1f}" +
                  f"\tannual: {100*compound_rate(worst, years):.2f}%" +
                  f" - {100*compound_rate(best, years):.2f}%")

    # generate the distribution of returns for specified period
    if period > 0:
        results = []
        final = len(sequences) - period
        for i in range(final):
            results.append(total_return(sequences, i, period))

        # bucketize the results for display
        granularity = bucketwidth(results)
        buckets = bucketize(results, granularity)
        offset = value_offset(results)
        (x_values, y_values) = distribution(buckets, granularity, offset)
        for i in range(len(x_values)):
            x_values[i] *= 100
            print(f"  {(x_values[i]):5.1f}    {y_values[i]}")
        plt.plot(x_values, y_values, "go")
        plt.title(TITLE + f" ({FIRST_YEAR}-{LAST_YEAR})")
        plt.xlabel(f"Total {period}-year Return (%)")
        plt.ylabel("probablity (%)")
        if OUTPUT is None:
            plt.show()
        else:
            print("Saving distribution plot as " + OUTPUT)
            plt.savefig(OUTPUT)
            plt.close()


# pylint: disable=C0103
if __name__ == "__main__":
    main(sys.argv[1:])
