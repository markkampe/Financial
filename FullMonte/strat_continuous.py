"""
Purchasing Strategy: continuous
"""
import statistics
import sys
import matplotlib.pyplot as plt
from market import Market
from buckets import bucketwidth, bucketize, distribution


# pylint: disable=R0801
def strat_continuous(sequence, period, monthly=False):
    """
    Buy a position over N years (or months)
    :param sequence: list of (growth, dividend, interest) tupples
    :param period(int): number of periods for buy-in
    :param monthly(bool): monthly (vs annual) sequence
    :return (float): value of position at end of simulation
    """

    in_market = 0.0     # start out with nothing in market
    on_side = 1.0       # start out with everything on the side
    lot = 1.0/period    # purchase uniformly over period

    for (growth, dividend, interest) in sequence:
        # if we are monthly, scale the interest and dividends
        if monthly:
            dividend /= 12
            interest /= 12

        # figure out how much everybody made this period
        in_market += in_market * (growth + dividend)
        on_side += on_side * interest

        # make our next purchase
        purchase = lot if lot <= on_side else on_side
        in_market += purchase
        on_side -= purchase

    return in_market + on_side


# general simulation parameters
NUM_RUNS = 50       # number of runs per model
NUM_YEARS = 20      # number of years to track results
MY_NAME = "Continuous Purchases"
OUTPUT = "Continuous.png"


# pylint: disable=too-many-locals
def main(random):
    """
    For purchases over 1-5 years,
        run <num_runs> simulations
        tracking output over 20 years
        plot a return distribution
    """

    # parameters specific to this continuous purchase model
    title = ("Random" if random else "Real sequence") + " simulations of "
    monthly = False     # annual simulations
    max_period = 5
    formats = ["w.", "r.", "y*", "go", "c+", "bx"]

    legends = []
    simulator = Market(monthly=monthly)
    # purchases spread out over 1-5 years
    for years in range(1, max_period + 1):
        results = []
        # a statistically interesting number of runs
        # pylint: disable=unused-variable
        for runs in range(NUM_RUNS * 2 if random else NUM_RUNS):
            sequence = simulator.rates(length=NUM_YEARS, random=random)
            results.append(strat_continuous(sequence, NUM_YEARS, monthly))

        # summarize the results
        mean = sum(results) / len(results)
        sigma = statistics.stdev(results)
        report = "{} over {} years, {} years: mean={:.2f}, sigma={:.2f}"
        print(report.format(MY_NAME, years, NUM_YEARS, mean, sigma))

        # bucketize and display the results
        granularity = bucketwidth(results)
        buckets = bucketize(results, granularity)
        (x_values, y_values) = distribution(buckets, granularity)

        plt.plot(x_values, y_values, formats[years])
        legends.append("over " + str(years) + " years")

    # put up the title, axes, and data
    plt.title(title + MY_NAME)
    plt.xlabel(str(NUM_YEARS) + "-year return")
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
