#!/usr/bin/python3
"""
Purchasing Strategy: all-in/all-out
"""
import statistics
import matplotlib.pyplot as plt
from market import Market
from buckets import bucketwidth, bucketize, distribution, value_offset
from compound import compound_rate


def strat_bottom(sequence, start, count, fractions, balance):
    """
    Buy at the lowest point in the sequence
    :param sequence: list of (price, dividend, interest) tupples
    :param start(int): starting index to process
    :param count(int): number of entries to process
    :param fractions(int): number of lots
           (if we are willingto buy at earlier lows)
    :param balance(float): total investment amount
    :return (float): value of position at end of simulation
    """
    # find the lowes prices in this market
    buy_points = [-1] * fractions
    for fract in range(fractions):
        for i in range(count):
            # ignore lows we've already found
            if i in buy_points:
                continue

            # is this a new low
            price = sequence[start + i][0]
            if buy_points[fract] == -1 or \
               price < sequence[buy_points[fract]][0]:
                buy_points[fract] = i

            # print(buy_points)

    # play through that purchase plan
    shares = 0
    purchase = balance/fractions
    for i in range(count):
        (price, dividend, interest) = sequence[start+i]
        if i in buy_points:
            shares += purchase/price
            balance -= purchase

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
MY_NAME = "Bottom-Buying"
OUTPUT = "Bottom.png"


# pylint: disable=too-many-locals
def main():
    """
    for a range of # lots
        run simulations over all 20 year sequences
            tracking total return
        plot a return distribution
    """

    # parameters specific to this continuous purchase model
    title = "Real sequence simulations of "

    legends = []
    formats = ["w.", "r.", "y+", "g*", "co"]

    # test all possible sequences
    simulator = Market(start=START, end=END)
    count = NUM_YEARS * 12
    last = len(simulator.data_points) - count
    for fractions in [1, 2, 3, 4]:
        results = []
        samples = 0
        for i in range(0, last):
            sequence = simulator.data_points
            results.append(strat_bottom(sequence, i, count, fractions,
                           BALANCE))
            samples += 1

        # summarize the results
        mean = sum(results) / len(results)
        sigma = statistics.stdev(results)
        rate = compound_rate(mean/BALANCE, NUM_YEARS)
        msg = MY_NAME
        msg += f" over {NUM_YEARS} years"
        msg += f" in {fractions} pieces:"
        msg += f" ({samples} runs)"
        msg += f": mean=${mean:,.0f}, sigma=${sigma:,.0f}"
        msg += f", return={100*rate:.2f}%/y"
        print(msg)

        # bucketize and display the results
        granularity = bucketwidth(results)
        buckets = bucketize(results, granularity)
        offset = value_offset(results)
        (x_values, y_values) = distribution(buckets, granularity, offset)

        plt.plot(x_values, y_values, formats[fractions])
        legends.append(f"fractions={fractions}")

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
