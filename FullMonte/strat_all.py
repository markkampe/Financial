from Market import Market
from buckets import *
import matplotlib.pyplot as plt
import statistics
import sys


"""
Purchasing Strategy: all-in/all-out
"""
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
        if (monthly):
            dividend /= 12
            interest /= 12

        if play_it_safe:
            balance += balance * interest
        else:
            balance += balance * (growth + dividend)

    return balance


# general simulation parameters
num_runs = 50       # number of runs per model
num_years = 20      # number of years to track results
my_name = "All-In/Out"

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
        for runs in range(num_runs * 2 if random else num_runs):
            sequence = simulator.rates(length=num_years, random=random)
            results.append( strat_all(sequence, in_cds, monthly) )

        # summarize the results
        mean = sum(results) / len(results)
        sigma = statistics.stdev(results)
        report = "{} {}, {} years value: mean={:.2f}, sigma={:.2f}"
        print(report.format(my_name, "CDs" if in_cds else "market", num_years, mean, sigma))

        # bucketize and display the results
        granularity = bucketwidth(results)
        buckets = bucketize(results, granularity)
        (x_values, y_values) = distribution(buckets, granularity)

        plt.plot(x_values, y_values, "go" if in_cds else "b*")
        legends.append("CDs" if in_cds else "market")

    # put up the title, axes, and data
    plt.title(title + my_name)
    plt.xlabel(str(num_years) + "-year return")
    plt.ylabel("probability")
    plt.legend(legends)
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "random":
        main(True)
    else:
        main(False)
