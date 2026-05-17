#!/usr/bin/python3
"""
Purchasing Strategy: buy on the dips
"""
import statistics
import matplotlib.pyplot as plt
from market import Market
from buckets import bucketwidth, bucketize, distribution, value_offset
from compound import compound_rate


# pylint: disable=too-many-locals, too-many-arguments
def strat_dips(sequence, start, count, max_dip, buy_points, balance):
    """
    Buy at the lowest point in the sequence
    :param sequence: list of (price, dividend, interest) tupples
    :param start(int): starting index to process
    :param count(int): number of entries to process
    :param max_dip(float): drop percent to trigger full buy-in
    :param buy_points(int): mow many buy points (max 4) we have
    :param balance(float): total investment amount
    :return (float): value of position at end of simulation
    """
    # figure out how much to buy at what thresholds (from max to min)
    thresholds = [max_dip] * buy_points     # threshold for each buy point
    purchases = [1.0] * buy_points          # how much of balance to spend
    # for max_dip=15%, buy_points=3
    #   thresholds = 0.15, 0.10, 0.05 -> -5%, -10%, -15%
    #   purchases  = 1.0,  0.5,  0.25 -> 1/4,  3/8,  3/8
    for i in range(1, buy_points):
        thresholds[i] = (buy_points-i) * max_dip / buy_points
        purchases[i] = purchases[i-1]/2

    # play through that purchase plan
    shares = 0
    market_max = 0
    for i in range(count):
        (price, dividend, interest) = sequence[start+i]
        if price > market_max:
            market_max = price

        # see if we have hit any buy points
        for i in range(0, buy_points):
            if (market_max - price)/market_max > thresholds[i]:
                spend = balance * purchases[i]
                shares += spend/price
                balance -= spend

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
MY_NAME = "Buy the Dips"
OUTPUT = "Dips.png"


def main():
    """
    for a range of # lots
        run simulations over all 20 year sequences
            tracking total return
        plot a return distribution
    """

    # parameters specific to this continuous purchase model
    title = "Real sequence simulations of "

    # mappings from parameters into point formats
    colors = {0.10: "r", 0.15: "y", 0.20: "g", 0.25: "c"}
    symbols = ["x", ".", "o", "+", "*"]
    legends = []

    # test all possible sequences
    simulator = Market(start=START, end=END)
    count = NUM_YEARS * 12
    last = len(simulator.data_points) - count

    # for a range of possible dip thresholds
    for max_dip in (0.10, 0.15, 0.20, 0.25):
        # for a number of sub-purchases we are willing to make
        for buy_points in [1, 2, 3]:
            results = []
            samples = 0
            for i in range(0, last):
                sequence = simulator.data_points
                results.append(strat_dips(sequence, i, count,
                               max_dip, buy_points, BALANCE))
                samples += 1

            # summarize the results
            mean = sum(results) / len(results)
            sigma = statistics.stdev(results)
            rate = compound_rate(mean/BALANCE, NUM_YEARS)
            msg = MY_NAME
            msg += f" ({100*max_dip:.0f}% dip/{buy_points})"
            msg += f" over {NUM_YEARS} years"
            msg += f" ({samples} runs)"
            msg += f": mean=${mean:6,.0f}, sigma=${sigma:6,.0f}"
            msg += f", return={100*rate:.2f}%/y"
            print(msg)

            # bucketize and display the results
            granularity = bucketwidth(results) * 2.0
            buckets = bucketize(results, granularity)
            offset = value_offset(results)
            (x_values, y_values) = distribution(buckets, granularity, offset)

            plt.plot(x_values, y_values, colors[max_dip] + symbols[buy_points])
            legends.append(f"{max_dip*100:.0f}% dip/{buy_points}")

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
