"""
Process historical data to generate a characterization (how much time
they spend how bad) of corrections.  Then compute the expected return
(probability * profit) of making investments at various discount levels.

Author: Mark Kampe
"""
import sys
import matplotlib.pyplot as plt


class Correction:
    """
    Process a set of (year, month, price) records to identify drops
    Produce a list of counts for how many times a drop (of a specified size)
    occurred within that history.
    """
    input_file = ""     # file used for simulations
    prices = []         # (year, month, price)

    def column(self, header, desired):
        """
        Helper to locate the desired field from a header line

        :param headers(str): header line
        :param desired(str): desired column heading
        :return (int): column number for desired field
        """
        fields = header.split(',')
        if desired in fields:
            return fields.index(desired)
        sys.stderr.write("Unable to find " + desired +
                         " column in " + self.input_file)
        sys.exit()

    # pylint: disable=too-many-arguments, too-many-locals
    def __init__(self, filename="sp500.csv",
                 start=1950, end=2020,
                 date_field="Date",
                 price_field="SP500",   # "Real Price" is inflation adjusted
                 date_format="y-m-d", ):
        """
        Instantiate a collection of price data

        :param filename: name of file containing return data
        :param start: first year of data to be used
        :param end:   last year of data to be used
        :param date_field: column heading for dates
        :param price_field: column heading for price
        :param date_format: date format
        """
        # pylint: disable=R1732     # don't want to indent next 50 lines
        source = open(filename, "r", encoding='ascii')

        # figure out which columns we want
        headers = source.readline()
        date_col = self.column(headers, date_field)
        price_col = self.column(headers, price_field)

        # figure out the date format
        delimiter = date_format[1]
        fields = date_format.split(delimiter)
        year_col = fields.index('y')
        if 'm' in fields:
            month_col = fields.index('m')

        # process the entire file
        prev = -1
        points = 0
        for line in source:
            fields = line.split(',')

            # make sure we have all of the expected data
            if fields[date_col] == "" or fields[price_col] == "":
                continue

            # extract the interesting fields
            price = float(fields[price_col])
            date = fields[date_col]
            date_fields = date.split(delimiter)
            year = int(date_fields[year_col])
            month = int(date_fields[month_col])
            if prev < 0:
                prev = price

            # see if this is within the requested range
            if start <= year <= end:
                tupple = (year, month, price)
                self.prices.append(tupple)
                prev = price
                points += 1

        source.close()

    def drop_buckets(self, bucket_width=.01):
        """
        Compute a density distribution for corrections of a given size

        :param bucket_widtn (fractional percentage): width of a bucket
        :return [(drop, count)]: # samples in each drop bucket
        """

        samples = []
        prev_high = -1
        for (_year, _month, price) in self.prices:
            # keep track of the previous high
            if price > prev_high:
                prev_high = price
                continue

            # (allocate and) increment the bucket for this drop
            drop_fraction = (prev_high - price) / prev_high
            bucket_num = int(drop_fraction/bucket_width)
            if bucket_num >= len(samples):
                for i in range(len(samples), bucket_num+1):
                    tupple = (i * bucket_width, 0)
                    samples.append(tupple)

            (bucket, count) = samples[bucket_num]
            samples[bucket_num] = (bucket, count+1)

        return samples


def analyze(buckets, width):
    """
    1. Review the data to identify corrections/crashes.
    2. Assess the probability of various drop levels.
    3. Compute the expected return (profit * probability) for each level.
    4. Assign fraction-to-purchase-at-that-discount proportional to expected
    """
    total_count = 0
    min_drop = 0.08
    max_drop = 0

    # how many (interesting) drop samples do we have
    for _index, (drop, count) in enumerate(buckets):
        if drop >= min_drop:
            total_count += count
        max_drop = int(100 * drop)

    # assemble arrays of drop/expected-profit points
    total_exp = 0.0
    drops = []
    expectancies = []
    for _index, (drop, count) in enumerate(buckets):
        if drop >= min_drop:
            drops.append(int(drop * 100))
            exp = drop * count / total_count
            expectancies.append(exp)
            total_exp += exp

    # plot expectancy vs drop
    plt.plot(drops, expectancies)
    plt.title("Buying-on-the-dips")
    plt.xlabel("drop percentage (" + str(int(100*width)) + "% buckets)")
    plt.xticks(range(0, max_drop, int(100 * width)))
    plt.ylabel("Expected Profit")

    # recommend purchanses in proportion to expectancy
    print("Recommended Purchases:")
    tot_pct = 0
    for index, drop in enumerate(drops):
        exp = expectancies[index]
        weight = int(100 * exp / total_exp)
        if weight <= 1:
            continue
        print(f"-{drop: >2}%:\t{weight: >3}%")
        tot_pct += weight
    print(f"    \t----\n    \t{tot_pct: >3}%")

    plt.show()


# basic exerciser
if __name__ == "__main__":
    # pylint: disable=C0103     # pylint thinks infile is a constant!
    if len(sys.argv) > 1:
        infile = sys.argv[1]
    else:
        infile = "sp500.csv"

    BUCKET_WIDTH = 0.04     # % per bucket

    results = Correction(infile)
    analyze(results.drop_buckets(bucket_width=BUCKET_WIDTH),
            width=BUCKET_WIDTH)
