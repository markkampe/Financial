#!/usr/bin/python3
"""
Purchasing Strategy: all-in/all-out
"""
import statistics
import matplotlib.pyplot as plt
from market import Market
from buckets import bucketwidth, bucketize, distribution, value_offset
from compound import compound_rate


def strat_all(sequence, start, count, play_it_safe, balance):
    """
    All in the market or all out of the market
    :param sequence: list of (price, dividend, interest) tupples
    :param start(int): starting index to process
    :param count(int): number of entries to process
    :param play_it_safe(bool): are we in market or CDs
    :param balance(float): total investment amount
    :return (float): value of position at end of simulation
    """

    # start with our initial allocation
    if play_it_safe:    # in CDs
        shares = 0
    else:               # in the market
        (price, dividend, interest) = sequence[start]
        shares = balance/price
        balance = 0.00

    # play through all the months in the count
    for i in range(count):
        (price, dividend, interest) = sequence[start + i]

        if play_it_safe:
            # we just earn interest
            balance += balance * interest/12
        else:
            # we reinvest (momthly) dividends
            shares += dividend/price

    # figure out the final acount value
    (price, _dividend, _interest) = sequence[start + count - 1]
    return balance + (shares * price)


# general simulation parameters
BALANCE = 1000.00   # initial balance
START = 1970
END = 2020
NUM_YEARS = 20      # number of years to track results
MY_NAME = "All-In/Out"
OUTPUT = "All.png"


# pylint: disable=too-many-locals
def main():
    """
    For all-in and all-out
        run simulations over 20 year sequences
            tracking total return
        plot a return distribution
    """

    # parameters specific to this continuous purchase model
    title = "Real sequence simulations of "

    legends = []
    simulator = Market(start=START, end=END)

    # purchases spread out over 1-5 years
    for in_cds in [True, False]:
        results = []

        # test all possible sequences
        count = NUM_YEARS * 12
        last = len(simulator.data_points) - count
        samples = 0
        for i in range(0, last):
            sequence = simulator.data_points
            results.append(strat_all(sequence, i, count, in_cds, 1000.00))
            samples += 1

        # summarize the results
        mean = sum(results) / len(results)
        sigma = statistics.stdev(results)
        rate = compound_rate(mean/BALANCE, NUM_YEARS)
        msg = MY_NAME
        msg += " CDs,   " if in_cds else " market,"
        msg += f" {NUM_YEARS} years"
        msg += f" ({samples} runs)"
        msg += f": mean=${mean:,.0f}, sigma=${sigma:,.0f}"
        msg += f", return={100*rate:.2f}%/y"
        print(msg)

        # bucketize and display the results
        granularity = bucketwidth(results)
        buckets = bucketize(results, granularity)
        offset = value_offset(results)
        (x_values, y_values) = distribution(buckets, granularity, offset)

        plt.plot(x_values, y_values, "go" if in_cds else "b*")
        legends.append("CDs" if in_cds else "market")

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
    main()
