"""
Purchasing Strategy: all-in/all-out
"""
import sys
import statistics
import matplotlib.pyplot as plt
from market import Market
from buckets import bucketwidth, bucketize, distribution


def strat_all(sequence, play_it_safe, monthly=False):
    """
    All in the market or all out of the market
    :param sequence: list of (growth, dividend, interest) tupples
    :param play_it_safe(bool): are we in market or CDs
    :param monthly(bool): monthly (vs annual) sequence
    :return (float): value of position at end of simulation
    """

    balance = 1.0

    for (growth, dividend, interest) in sequence:
        # if we are monthly, scale the interest and dividends
        if monthly:
            dividend /= 12
            interest /= 12

        if play_it_safe:
            balance += balance * interest
        else:
            balance += balance * (growth + dividend)

    return balance


# general simulation parameters
NUM_RUNS = 50       # number of runs per model
NUM_YEARS = 20      # number of years to track results
MY_NAME = "All-In/Out"
OUTPUT = "All.png"


# pylint: disable=too-many-locals
def main(random):
    """
    For all-in and all-out
        run <num_runs> simulations
        tracking output over 20 years
        plot a return distribution
    """

    # parameters specific to this continuous purchase model
    title = ("Random" if random else "Real sequence") + " simulations of "
    monthly = False     # annual simulations

    legends = []
    simulator = Market(monthly=monthly)

    # purchases spread out over 1-5 years
    for in_cds in [True, False]:
        results = []
        # a statistically interesting number of runs
        for _runs in range(NUM_RUNS * 2 if random else NUM_RUNS):
            sequence = simulator.rates(length=NUM_YEARS, random=random)
            results.append(strat_all(sequence, in_cds, monthly))

        # summarize the results
        mean = sum(results) / len(results)
        sigma = statistics.stdev(results)
        report = "{} {}, {} years: mean={:.2f}, sigma={:.2f}"
        print(report.format(MY_NAME, "CDs" if in_cds else "market",
              NUM_YEARS, mean, sigma))

        # bucketize and display the results
        granularity = bucketwidth(results)
        buckets = bucketize(results, granularity)
        (x_values, y_values) = distribution(buckets, granularity)

        plt.plot(x_values, y_values, "go" if in_cds else "b*")
        legends.append("CDs" if in_cds else "market")

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
