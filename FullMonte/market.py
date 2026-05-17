#!/usr/bin/python3
"""
A market data digester

Author: Mark Kampe
"""
import sys
from compound import compound_rate


class Market:
    """
    Digest a file of market quotes, extract the entries between
    a set of specified dates, and preoduce a simpler sequence
    of monthly (price, dividend, interest rate) tupples.
    """
    input_file = ""     # file used for simulations
    data_points = []

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
                 price_field="SP500",       # inflation adjusted dollars
                 div_field="Dividend",      # inflation adjusted dollars
                 int_field="Long Interest Rate",    # percentage
                 date_format="y-m-d", ):
        """
        Instantiate a new simulator

        :param filename: name of file containing return data
        :param start: first year of data to be used
        :param end:   last year of data to be used
        :param date_field: column heading for dates
        :param price_field: column heading for price
        :param date_format: date format
        """
        # re-initialize the output array
        self.data_points = []
        expected = (end + 1 - start) * 12

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
        rate_sum = 0
        div_sum = 0
        points = 0
        line_num = 1
        first_price = -666.0
        last_price = -666.0
        for line in source:
            line_num += 1
            fields = line.split(',')

            # make sure we have all of the expected data
            if (fields[date_col] == "" or fields[price_col] == "" or
               fields[div_col] == "" or fields[rate_col] == ""):
                sys.stderr.write(f"{line_num}: missing data fields\n")
                continue

            # pull out the date to see if it qualifies
            date = fields[date_col]
            date_fields = date.split(delimiter)
            year = int(date_fields[year_col])
            month = int(date_fields[month_col])

            # we will need to know the last price before our start
            price = float(fields[price_col])    # dollars

            # see if this is within the requested range
            if start <= year <= end:
                # pull out the price, dividend and interest rates
                div = float(fields[div_col])        # this is an annual number
                rate = float(fields[rate_col])      # long rate (as percentage)

                # we record all of these as fractional values
                tupple = (price, div/12, rate/100)
                self.data_points.append(tupple)

                # accumulate statistics for the whole sequence
                if year == start and month == 1:
                    first_price = price
                elif year == end and month == 12:
                    last_price = price
                div_sum += div/price
                rate_sum += rate/100
                points += 1

        # summarize what we just read
        ret_pct = 100 * compound_rate(last_price/first_price, end + 1 - start)
        div_pct = 100 * div_sum / points
        rate_pct = 100 * rate_sum / points
        print(filename +
              f"({start}-{end}): {points}/{expected} monthly data points" +
              f", growth={ret_pct:3.1f}%" +
              f", div={div_pct:2.1f}%" +
              f", int(10y)={rate_pct:2.1f}%")
        source.close()

    def t_dump(self, index):
        """ format a tupple for printing """
        (price, dividend, int_rate) = self.data_points[index]
        return f"${price:9.2f}" +          \
               f"\t${dividend*12:7.2f}" +   \
               f"\t{int_rate*100:7.2f}%"


def main(infile):
    """
    basic exercise of market data extraction

    :param infile(string): neme of input file
    """
    # test data to be extracted and printed
    year_start = 1950     # well after start
    year_end = 2000       # well before end
    year_test = 1970      # mid-range
    num_years = 20        # months to print

    simulator = Market(infile, start=year_start, end=year_end)
    print()
    print(f"Monthly sequenced return data from {infile}" +
          f", beginning 01/01/{year_test}")
    print("  (Compare the following with the same months from that file)")
    print()

    heading = "       date   \t     price\tdividend\tinterest\n" +\
              "    ----------\t----------\t--------\t--------"
    print(heading)
    base = (year_test - year_start) * 12
    for i in range(num_years):
        year = int((base + i)/12) + year_start
        month = 1 + ((base + i) % 12)

        print(f"    {month:2}/01/{year:4}\t" + simulator.t_dump(base + i))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main("sp500.csv")
