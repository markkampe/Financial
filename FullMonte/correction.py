#!/usr/bin/python3
"""
Process historical data to generate a characterization (how much time
they spend how bad) of corrections.  Then compute the expected return
(probability * profit) of making investments at various discount levels.

Author: Mark Kampe
"""
import argparse
import matplotlib.pyplot as plt
from market import Market

START = 1950            # first year of samples to use
END = 2020              # last year of samples to use
MAX_DROP = 1.0          # 100% is worst possible drop
OUTPUT = "Corrections"


def drop_buckets(sequence, bucket_width=.01):
    """
    Compute a density distribution for corrections of a given size
    :param sequence: list of monthly (price, dividend, interest) tupples
    :param bucket_widtn (fractional percentage): width of a bucket
            note that larger buckets accomplish curve smoothing
            which is valuable for relatively thin data
    :return [(drop, count)]: # samples in each drop bucket
    """
    # allocate a list of buckets (with specified width)
    num_buckets = int(MAX_DROP/bucket_width)
    samples = [(0, 0)] * num_buckets
    for i in range(num_buckets):
        samples[i] = (i * bucket_width, 0)

    # enumerate all drops after  highs
    prev_high = -1
    for (price, _div, _interest) in sequence:
        # keep track of the previous high
        if price > prev_high:
            prev_high = price
            continue

        # not a high: increment the bucket for this drop
        drop_fraction = (prev_high - price) / prev_high
        bucket_num = int(drop_fraction/bucket_width)
        (bucket, count) = samples[bucket_num]
        samples[bucket_num] = (bucket, count+1)

    # truncate the unused bucekts at the end of the list
    while samples[num_buckets - 1][1] == 0:
        num_buckets -= 1
    del samples[num_buckets:]

    return samples


# pylint: disable=too-many-locals, too-many-statements
def analyze(buckets, width, optimism):
    """
    1. Review the data to identify corrections/crashes.
    2. Assess the probability of various drop levels.
    3. Compute the expected return (profit * probability) for each level.
    4. Assign fraction-to-purchase-at-that-discount proportional to expected
    :param buckets ([int]): list of bucket counts
    :param width (float): fractional bucket width
    :param optimism (float): fractional optimism threhshold
    """
    total_count = 0
    min_drop = 0.08

    # how many (interesting) drop samples do we have
    for _index, (drop, count) in enumerate(buckets):
        if drop >= min_drop:
            total_count += count

    # assemble arrays of drop/expected-profit points
    opt_exp = 0.0       # total if we are optimistic
    pess_exp = 0.0      # total if we are pessimistic

    drops = []
    probabilities = []
    expectancies = []
    for _index, (drop, count) in enumerate(buckets):
        if drop >= min_drop:
            drops.append(int(drop * 100))

            prob = count / total_count
            probabilities.append(int(prob*100))

            exp = 100 * (drop * prob)
            expectancies.append(exp)
            opt_exp += exp
            if prob >= optimism:
                pess_exp += exp

    # first curve is probability of a drop
    fig, ax1 = plt.subplots()
    plt.title("Profitability of waiting for a dip")
    ax1.set_xlabel(f"drop percentage ({int(100*width)}% buckets)")
    ax1.set_ylabel("Probability (%)", color='b')
    ax1.plot(drops, probabilities, 'b')

    # second curve is expectancy of waiting for it
    ax2 = ax1.twinx()
    ax2.set_ylabel("Profit Expectancy (%)", color='g')
    ax2.plot(drops, expectancies, 'g')

    fig.tight_layout()
    if OUTPUT is None:
        plt.show()
    else:
        print("saving distribution plot as " + OUTPUT + ".png")
        plt.savefig(OUTPUT)
        plt.close()

    # recommend purchanses in proportion to expectancy
    print("Recommendations:")
    print("   Larger dips are more profitable but less likely, making")
    print("   holding out for a larger dip a potentially dodgy proposition.")
    print("   Thus, the amount we plan to invest after each dip should be")
    print("   proportional, not to possible profit, but to its expectancy.")
    print("   The following table suggests what fraction of our opportunity")
    print("   cash we might choose to invest after dips of various levels.")
    print()
    print("     drop  prob  greed   fear*")
    print("    -----  ----  -----  -----")
    tot_opt = 0
    tot_pess = 0
    tot_prob = 0
    for index, drop in enumerate(drops):
        prob = probabilities[index]
        tot_prob += prob
        exp = expectancies[index]       # percentage (not fraction)
        o_weight = int(100 * exp / opt_exp)
        if o_weight <= 1:
            continue
        tot_opt += o_weight
        p_weight = 0 if prob < optimism * 100 else int(100 * exp / pess_exp)
        tot_pess += p_weight
        print(f"     -{drop: >2}%  {prob: >3}%   {o_weight: >3}%" +
              f"   {p_weight: >3}%")

    print("           ----  -----  -----")
    print(f"           {tot_prob:>3}%   {tot_opt:>3}%   {tot_pess:>3}%")
    print()
    print(f"  *The fear recommendations ignore drops with P < {optimism:.3f}")


def main(infile, width, optimism):
    """
    exerciser
    :param args (string): name of market data file
    """

    simulator = Market(infile, start=START, end=END)
    buckets = drop_buckets(simulator.data_points, bucket_width=width)
    analyze(buckets, width=width, optimism=optimism)


# basic exerciser
if __name__ == "__main__":
    DESCR = 'Market dip probability/expectancy analysis'
    parser = argparse.ArgumentParser(description=DESCR)
    parser.add_argument("file", nargs="?", default="sp500.csv",
                        help="market history CSV file")
    parser.add_argument("-w", "--width", type=int, default=5,
                        help="(integer percentage) bucket width")
    parser.add_argument("-o", "--optimism", type=int, default=10,
                        help="(integer percentage) optimisim cut-off")
    args = parser.parse_args()

    main(args.file, args.width/100, args.optimism/100)
