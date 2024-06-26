from Market import Market
from buckets import *
import matplotlib.pyplot as plt
import statistics
import sys

"""
Purchasing Strategy: by at the bottom
"""


def strat_bottom(sequence, fractions, monthly=True):
    """
    Only buy at the lowest prices
    :param sequence: list of (growth, dividend, interest) tupples
    :param fractions(int): max number of lots
           (we are willing to buy in at earlier lows)
    :param monthly(bool): monthly (vs annual) sequence
    :return (float): value of position at end of simulation
    """

    # find the absolute bottom
    buypoints = [0] * fractions
    bottom = 666.0
    market = 1.0
    for i in range(len(sequence)):
        (growth, dividend, interest) = sequence[i]
        market *= (1 + growth)
        if market < bottom:
            bottom = market
            buypoints[0] = i

    # find the buy points before that
    for f in range(1, fractions):
        buypoints[f] = 0
        bottom = 666.0
        market = 1.0

        # see if we have run out of opportunities
        if buypoints[f-1] == 0:
            fractions = f
            break

        # find the next lowest earlier price
        for i in range(buypoints[f-1]):
            (growth, dividend, interest) = sequence[i]
            market *= (1 + growth)
            if market < bottom:
                bottom = market
                buypoints[f] = i

    # play the sequence, buying in at the bottom
    in_market = 0.0     # start out with nothing in market
    on_side = 1.0       # start out with everything on the side

    for i in range(len(sequence)):
        (growth, dividend, interest) = sequence[i]

        # see if this is a buy point
        if i in buypoints:
            in_market += on_side/fractions
            on_side -= on_side/fractions

        # if we are monthly, scale the interest and dividends
        if (monthly):
            dividend /= 12
            interest /= 12

        # figure out how much everybody made this period
        in_market += in_market * (growth + dividend)
        on_side += on_side * interest

    return in_market + on_side


# general simulation parameters
num_runs = 200      # number of runs per model
num_years = 20      # number of years to track results
my_name = "Bottom-Buying"
output = "Bottom.png"


def main(random):
    """
    Only buy in at lows
        run <num_runs> simulations
        tracking output over 20 years
        plot a return distribution
    """

    # parameters specific to this continuous purchase model
    title = ("Random" if random else "Real sequence") + " simulations of "
    monthly = True     # monthly simulations
    formats = ["w.", "r.", "y+", "g*", "co"]

    legends = []
    simulator = Market(monthly=monthly)
    for fractions in [1, 2, 3, 4]:
        results = []
        # a statistically interesting number of runs
        for runs in range(num_runs * 2 if random else num_runs):
            sequence = simulator.rates(length=num_years*12, random=random)
            results.append(strat_bottom(sequence, fractions, monthly))

        # summarize the results
        mean = sum(results) / len(results)
        sigma = statistics.stdev(results)
        report = "{} over {} years in {} pieces: mean={:.2f}, sigma={:.2f}"
        print(report.format(my_name, num_years, fractions, mean, sigma))

        # bucketize and display the results
        granularity = bucketwidth(results)
        buckets = bucketize(results, granularity)
        (x_values, y_values) = distribution(buckets, granularity)

        plt.plot(x_values, y_values, formats[fractions])
        legends.append("fractions=" + str(fractions))

    # put up the title, axes, and data
    plt.title(title + my_name)
    plt.xlabel(str(num_years) + "-year return")
    plt.ylabel("probability")
    plt.legend(legends)
    if output is None:
        plt.show()
    else:
        print("saving distribution plot as " + output)
        plt.savefig(output)
        plt.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "random":
        main(True)
    else:
        main(False)
