#!/usr/bin/python3
"""
Market Returns: best and worst
"""
import sys
import statistics
import matplotlib.pyplot as plt
from market import Market
from buckets import bucketwidth, bucketize, distribution, value_offset
from compound import compound_rate


def total_return(sequence, start, count, balance):
    """
    All in the market or all out of the market
    :param sequence: list of (price, dividend, interest) tupples
    :param start(int): starting index to process
    :param count(int): number of entries to process
    :return (float): value of position at end of simulation
    """
    # start with our initial allocation
    (price, dividend, _interest) = sequence[start]
    shares = balance/price
    balance = 0.00

    # play through all the months in the count
    for i in range(count):
        (price, dividend, _interest) = sequence[start + i]
        # we reinvest (monthly) dividends
        shares += shares * dividend/price

    # figure out the final acount value
    (price, _dividend, _interest) = sequence[start + count - 1]
    return balance + (shares * price)


# general simulation parameters
BALANCE = 1000.00   # initial balance
START = 1970
END = 2020
MY_NAME = "Duration"
OUTPUT = "Duration.png"


def date(index):
    """ turn a sequence index into a month/year """
    year = int(START + (index/12))
    month = int(index % 12)
    return f"{month}/{year:4}"


# pylint: disable=too-many-locals, too-many-statements, too-many-branches
def main(args):
    """
    For all-in and all-out
        run simulations over 20 year sequences
            tracking total return
        plot a return distribution
    """
    verbose = False
    for _i, arg in enumerate(args):
        if arg in ('-v', '--verbose'):
            verbose = True

    # parameters specific to this continuous purchase model
    simulator = Market(start=START, end=END)

    # purchases spread out over 1-5 years
    for years in (1, 2, 3, 4, 5, 6, 8, 10, 15, 20):
        results = []
        total = 0.0
        best = -666.666
        worst = 6666666.666
        worstx = -1
        uw = 0

        # test all possible sequences
        count = years * 12
        last = len(simulator.data_points) - count
        samples = 0
        for i in range(0, last):
            sequence = simulator.data_points
            result = total_return(sequence, i, count, BALANCE)
            total += result
            if result > best:
                best = result
            if result < worst:
                worst = result
                worstx = i
            samples += 1
            if result < BALANCE:
                uw += 1
            results.append(result)

        # summarize the results
        mean = sum(results) / len(results)
        sigma = statistics.stdev(results)
        rate = compound_rate(mean/BALANCE, years)
        msg = "  " + MY_NAME
        msg += f" {years:2} years"
        if verbose:
            msg += f" ({samples} runs)"
        msg += f":\t${worst:6,.0f} - ${best:6,.0f}"
        msg += f",  mean=${mean:,.0f}, sigma={sigma:4.0f}"
        msg += f", {100*rate:.2f}%/y"
        if uw > 0:
            msg += f" ({uw}/{samples} negative outcomes"
            if verbose:
                msg += f", worst {date(worstx)} - {date(worstx+count-1)}"
            msg += ")"
        print(msg)

    # gnerate a distribution of 5-year results
    legends = []
    for years in (5, 10):
        results = []
        count = years * 12
        last = len(simulator.data_points) - count
        samples = 0
        for i in range(0, last):
            sequence = simulator.data_points
            results.append(total_return(sequence, i, count, BALANCE))

        # bucketize and display the results
        granularity = bucketwidth(results)
        buckets = bucketize(results, granularity)
        offset = value_offset(results)
        (x_values, y_values) = distribution(buckets, granularity, offset)

        plt.plot(x_values, y_values, "go" if years == 5 else "b*")
        legends.append(f"{years} years")

    # put up the title, axes, and data
    plt.title(f"Return on investment of ${BALANCE:,.0f}")
    plt.xlabel("value at end of period")
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
