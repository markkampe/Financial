#!/usr/bin/python3
"""
A market return simulator, based on historical data

Author: Mark Kampe
"""
import sys
from random import randint


class Market:
    """
    Digest a file of market quotes (w/date, dividend, price) data
    Based on which we can return randomly chosen sequences of returns
    """
    input_file = ""     # file used for simulations

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
        # re-initialize the output array
        self.data_points = []

        # pylint: disable=R1732     # I don't want to indent the next 50 lines
        source = open(filename, "r", encoding='ascii')

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
        prev = 0
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

            # pull out the date to see if it qualifies
            date = fields[date_col]
            date_fields = date.split(delimiter)
            year = int(date_fields[year_col])
            month = int(date_fields[month_col])

            # we will need to know the last price before our start
            price = float(fields[price_col])    # dollars
            if year < start and (monthly or month == 1):
                prev = price

            # see if this is within the requested range
            if start <= year <= end:
                # see if we are doing only annual samples
                if month != 1 and not monthly:
                    continue

                # pull out the price, dividend and interest rates
                appreciation = price - prev         # $
                div = float(fields[div_col])        # $ interp from 4Q totals
                rate = float(fields[rate_col])      # % long rate

                # we record all of these as fractional values
                tupple = (appreciation/prev, div/price, rate/100)
                self.data_points.append(tupple)
                prev = price

                # accumulate statistics for the whole sequence
                ret_sum += appreciation/prev
                div_sum += div/price
                rate_sum += rate/100
                points += 1

        # summarize what we just read
        period = "monthly" if monthly else "annual"
        ret_pct = 100 * ret_sum / points * (12 if monthly else 1)
        div_pct = 100 * div_sum / points
        rate_pct = 100 * rate_sum / points
        print(filename +
              f"({start}-{end}): {points} {period} data points" +
              f", growth={ret_pct:3.1f}%" +
              f", div={div_pct:2.1f}%" +
              f", int(10y)={rate_pct:2.1f}%")
        source.close()

    def rates(self, length=20, random=False):
        """
        return a (randomly chosen) list of market performance tupples

        :param length: number of desired prices
        :param random: random order (vs real sequences)
        :return: list of price changes (appreciation, dividend, long rate)
        """
        size = len(self.data_points)
        if random:
            # return random values
            return [self.data_points[randint(0, size - 1)]
                    for i in range(0, length)]
        # return consecutive values w/random starting point
        first = randint(0, size - 1)
        return [self.data_points[(first + i) % size]
                for i in range(0, length)]

    def chosen(self, first=0, length=0):
        """
        return a (contiguous) subset of the list

        :param first: index of first desired element
        :param length: number of desired elements
        :return: list of data points
        """
        # figure out how many items to return
        if length == 0:
            length = len(self.data_points) - first

        return [self.data_points[first + i]
                for i in range(0, length)]


def t_dump(app_rate, div_rate, int_rate):
    """ format a tupple for printing """
    return f"\t{app_rate*100:11.3f}%" +    \
           f"\t{div_rate*100:7.2f}%" +   \
           f"\t{int_rate*100:7.2f}%"


# basic exerciser
if __name__ == "__main__":
    # pylint: disable=C0103     # pylint thinks infile is a constant!
    if len(sys.argv) > 1:
        infile = sys.argv[1]
    else:
        infile = "sp500.csv"

    START = 1950
    END = 2020

    heading = "\tappreciation\tdividend\tinterest\n" +\
              "\t------------\t--------\t--------"

    for by_month in [False, True]:
        simulator = Market(infile, start=START, end=END, monthly=by_month)

        for do_random in [False, True]:
            print(("Monthly " if by_month else "Annual ") +
                  ("random return" if do_random else "sequenced return") +
                  " simulation based on " + infile)

            sequence = simulator.rates(random=do_random)
            print(heading)
            for (delta, dividend, interest) in sequence:
                print(t_dump(delta, dividend, interest))
            print("")

        print(("Monthly " if by_month else "Annual ") +
              ("chosen sequence return") +
              f" starting with {START+1}-01-01" +
              " based on " + infile)

        # choose a known sequence for easy testing
        first_sample = 12 if by_month else 1
        sequence = simulator.chosen(first_sample, length=20)
        print(heading)
        for (delta, dividend, interest) in sequence:
            print(t_dump(delta, dividend, interest))
        print("")
