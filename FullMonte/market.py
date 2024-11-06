"""
A market return simulator, based on historical data

Author: Mark Kampe
"""
import sys
from random import randint


# pylint: disable=R0801     # correction and market are very similar
class Market:
    """
    FIX
    """
    input_file = ""     # file used for simulations
    data_points = []    # (appreciation, dividend, interest rate)

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
                 monthly=False,
                 start=1950, end=2020,
                 date_field="Date",
                 price_field="SP500",       # inflation adjusted
                 div_field="Dividend",      # inflation adjusted
                 int_field="Long Interest Rate",
                 date_format="y-m-d", ):
        """
        Instantiate a new simulator

        :param filename: name of file containing return data
        :param monthly: monthly (vs annual) prices
        :param start: first year of data to be used
        :param end:   last year of data to be used
        :param date_field: column heading for dates
        :param price_field: column heading for price
        :param date_format: date format
        """
        source = open(filename, "r")

        # figure out which columns we want
        headers = source.readline()
        date_col = self.column(headers, date_field)
        price_col = self.column(headers, price_field)
        div_col = self.column(headers, div_field)
        rate_col = self.column(headers, int_field)

        # figure out the date format
        delimiter = date_format[1]
        fields = date_format.split(delimiter)
        year_col = fields.index('y')
        if 'm' in fields:
            month_col = fields.index('m')

        # process the entire file
        prev = -1
        rate_sum = 0
        div_sum = 0
        ret_sum = 0
        points = 0
        for line in source:
            fields = line.split(',')

            # make sure we have all of the expected data
            if (fields[date_col] == "" or fields[price_col] == "" or
               fields[div_col] == "" or fields[rate_col] == ""):
                continue

            # extract the interesting fields
            price = float(fields[price_col])
            div = float(fields[div_col])
            rate = float(fields[rate_col])
            date = fields[date_col]
            date_fields = date.split(delimiter)
            year = int(date_fields[year_col])
            month = int(date_fields[month_col])
            if prev < 0:
                prev = price

            # see if this is within the requested range
            if year >= start and year <= end:
                # see if we are doing only annual samples
                if month != 1 and not monthly:
                    continue
                appreciation = (price - prev)/prev
                tupple = (appreciation, div/price, rate/100)
                self.data_points.append(tupple)
                prev = price

                # and accumulate statistics
                ret_sum += 12 * appreciation if monthly else appreciation
                div_sum += div/price
                rate_sum += rate/100
                points += 1

        # summarize what we just read
        period = "monthly" if monthly else "annual"
        print(filename +
              "({}-{}): {} {} data points".format(start, end, points, period) +
              ", growth={:3.1f}%".format(100 * ret_sum / points) +
              ", div={:2.1f}%".format(100 * div_sum / points) +
              ", 10Y={:2.1f}%".format(100 * rate_sum / points))
        source.close()

    def rates(self, length=20, random=False):
        """
        return a list of market performance tupples

        :param length: number of desired prices
        :param random: random order
        :return: list of price changes (appreciation, dividend, long rate)
        """
        size = len(self.data_points)

        if random:
            # return random values
            return [self.data_points[randint(0, size - 1)]
                    for i in range(0, length)]
        # return consecutive values w/random starting point
        start = randint(0, size - 1)
        return [self.data_points[(start + i) % size]
                for i in range(0, length)]


# basic exerciser
if __name__ == "__main__":
    # pylint: disable=C0103     # this is a variable!
    if len(sys.argv) > 1:
        infile = sys.argv[1]
    else:
        infile = "sp500.csv"

    START = 2017
    END = 2020

    heading = "\tappreciation\tdividend\tinterest\n" +\
              "\t------------\t--------\t--------"

    OUTPUT = "\t{:12.8f}\t{:8.4f}\t{:8.4f}"

    for by_month in [False, True]:
        simulator = Market(infile, start=START, end=END, monthly=by_month)

        for do_random in [False, True]:
            print(("Monthly " if by_month else "Annual ") +
                  ("random return" if do_random else "sequenced return") +
                  " simulation based on " + infile)

            sequence = simulator.rates(random=do_random)
            print(heading)
            for (delta, dividend, interest) in sequence:
                print(OUTPUT.format(delta, dividend, interest))
            print("")
