#!/usr/bin/python3
"""
Purchasing Strategy: continuous over time
"""
import sys
import statistics
import matplotlib.pyplot as plt
from market import Market
from buckets import bucketwidth, bucketize, distribution, value_offset
from compound import compound_rate


def strat_continuous(sequence, start, count, period, balance):
    """
    Buy uniformly over the period
    :param sequence: list of (price, dividend, interest) tupples
    :param start(int): starting index to process
    :param count(int): number of entries to process
    :param period(int): months over which we make our purchases
    :param balance(float): total investment amount
    :return (float): value of position at end of simulation
    """
    # play through that purchase plan
    shares = 0
    purchase = balance/period
    for i in range(count):
        (price, dividend, interest) = sequence[start+i]

        if balance > 0:
            purch = min(balance, purchase/price)
            shares += purch/price
            balance -= purch

        # every year reinvests dividends
        if shares > 0:
            shares += shares * dividend/price

        # every year earns interest
        balance += balance * interest/12

    # figure out the final acount value
    (price, _dividend, _interest) = sequence[start + count - 1]
    return balance + (shares * price)


# general simulation parameters
BALANCE = 1000.00   # initial balance
START = 1970
END = 2020
NUM_YEARS = 20      # number of years to track results
MAX_PERIOD = 5      # max years over which to purchase
MY_NAME = "Continuous Purchases"
OUTPUT = "Continuous.png"


# pylint: disable=too-many-locals
def main(args):
    """
    for a range of # lots
        run simulations over all 20 year sequences
            tracking total return
        plot a return distribution
    """
    verbose = False
    for _i, arg in enumerate(args):
        if arg in ('-v', '--verbose'):
            verbose = True

    # parameters specific to this continuous purchase model
    title = "Real sequence simulations of "

    legends = []
    formats = ["w.", "r.", "y*", "go", "c+", "bx"]

    # test all possible sequences
    simulator = Market(start=START, end=END)
    count = NUM_YEARS * 12
    last = len(simulator.data_points) - count
    for period in range(1, MAX_PERIOD+1):
        results = []
        samples = 0
        for i in range(0, last):
            seq = simulator.data_points
            results.append(strat_continuous(seq, i, count, period, BALANCE))
            samples += 1

        # summarize the results
        mean = sum(results) / len(results)
        sigma = statistics.stdev(results)
        rate = compound_rate(mean/BALANCE, NUM_YEARS)
        msg = MY_NAME
        msg += f" over {period} years"
        if verbose:
            msg += f" ({samples} runs)"
        msg += f": mean=${mean:,.0f}, sigma=${sigma:,.0f}"
        msg += f", return={100*rate:.2f}%/y"
        print(msg)

        # bucketize and display the results
        granularity = bucketwidth(results)
        buckets = bucketize(results, granularity)
        offset = value_offset(results)
        (x_values, y_values) = distribution(buckets, granularity, offset)

        plt.plot(x_values, y_values, formats[period])
        legends.append(f"over {period} years")

    # put up the title, axes, and data
    plt.title(title + MY_NAME)
    plt.xlabel(f" {NUM_YEARS}-year return on ${BALANCE:,.0f}")
    plt.ylabel("probability")
    plt.legend(legends)
    if OUTPUT is None:
        plt.show()
    else:
        print("saving distribution plot as " + OUTPUT)
        plt.savefig(OUTPUT)
        plt.close()


if __name__ == "__main__":
    main(sys.argv[1:])
