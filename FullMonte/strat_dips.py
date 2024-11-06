"""
Purchasing Strategy: Buy on the dips
"""
import statistics
import sys
import matplotlib.pyplot as plt
from market import Market
from buckets import bucketwidth, bucketize, distribution


# pylint: disable=R0801     # all strat modules have same form
def strat_dips(sequence, max_dip, buy_points, monthly=True):
    """
    Only buy at the lowest prices
    :param sequence: list of (growth, dividend, interest) tupples
    :param max_dip(float): drop percent to trigger full buy-in
    :param buy_points(int): how many (max/4) buy points do we have
    :param monthly(bool): monthly (vs annual) sequence
    :return (float): value of position at end of simulation
    """

    # figure out how much to buy at what thresholds (from max to min)
    thresholds = [max_dip] * buy_points
    purchases = [1.0] * buy_points
    for i in range(1, buy_points):
        thresholds[i] = (buy_points-i) * max_dip / buy_points
        purchases[i] = purchases[i-1]/2

    # play the sequence, buying on the dips
    in_market = 0.0     # start out with nothing in market
    on_side = 1.0       # start out with everything on the side
    market = 1.0        # initial market valuation
    market_max = 1.0    # highest valuation I have seen

    for (growth, dividend, interest) in sequence:

        # calculate value and keep track of max value
        market += market * growth
        if market > market_max:
            market_max = market

        # see if we have hit any buy points
        for i in range(0, buy_points):
            if (market_max - market)/market_max > thresholds[i]:
                in_market += on_side * purchases[i]
                on_side -= on_side * purchases[i]
                break

        # if we are monthly, scale the interest and dividends
        if monthly:
            dividend /= 12
            interest /= 12

        # figure out how much everybody made this period
        in_market += in_market * (growth + dividend)
        on_side += on_side * interest

    return in_market + on_side


# general simulation parameters
NUM_RUNS = 200      # number of runs per model
NUM_RUNS = 20      # number of years to track results
MY_NAME = "Buy the Dips"
OUTPUT = "Dips.png"


# pylint: disable=too-many-locals
def main(random):
    """
    Buy on the dips
        run <NUM_RUNS> simulations
        tracking output over 20 years
        plot a return distribution
    """

    # parameters specific to this continuous purchase model
    title = ("Random" if random else "Real sequence") + " simulations of "
    monthly = True     # monthly simulations

    # mappings from parameters into point formats
    colors = {0.10: "r", 0.15: "y", 0.20: "g", 0.25: "c"}
    symbols = ["x", ".", "o", "+", "*"]

    legends = []
    simulator = Market(monthly=monthly)
    # for a range of plausible dip thresholds
    for max_dip in (0.10, 0.15, 0.20, 0.25):
        # are we willing to buy part on smaller dips
        for buy_points in [1, 2, 3]:
            results = []
            # a statistically interesting number of runs
            # pylint: disable=unused-variable
            for runs in range(NUM_RUNS * 2 if random else NUM_RUNS):
                sequence = simulator.rates(length=NUM_RUNS*12, random=random)
                results.append(strat_dips(sequence, max_dip, buy_points,
                               monthly))

            # summarize the results
            mean = sum(results) / len(results)
            sigma = statistics.stdev(results)
            report = "{}({}%/{}) over {} years: mean={:.2f}, sigma={:.2f}"
            print(report.format(MY_NAME,
                  int(100*max_dip), buy_points, NUM_RUNS, mean, sigma))

            # bucketize and display the results
            granularity = bucketwidth(results)
            buckets = bucketize(results, granularity)
            (x_values, y_values) = distribution(buckets, granularity)

            plt.plot(x_values, y_values, colors[max_dip] + symbols[buy_points])
            legends.append(str(int(max_dip*100)) + "% dip/" + str(buy_points))

        print("")   # blank line between changes in threshold

    # put up the title, axes, and data
    plt.title(title + MY_NAME)
    plt.xlabel(str(NUM_RUNS) + "-year return")
    plt.ylabel("probability")
    plt.legend(legends)
    if OUTPUT is None:
        plt.show()
    else:
        print("saving distribution plot as " + OUTPUT)
        plt.savefig(OUTPUT)
        plt.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "random":
        main(True)
    else:
        main(False)
