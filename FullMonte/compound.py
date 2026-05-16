#!/usr/bin/python3
"""
A compound interest computation

Author: Mark Kampe
"""


def compound_interest(rate, years):
    """
    compute compound interest multiplier

    :param rate(float): as a fraction (0.0-1.0)
    :param years(int):  number of years of compounding
    :return (float):    what 1.0 would compound to
    """
    balance = 1.0
    for _ in range(years):
        balance *= (1.0 + rate)

    return balance


def compound_rate(value, years):
    """
    figure out the rate that would yield an appreciation
    :param value(float):    value of 1.0 after specified years
    :param years(int):      number of years of compounding
    return (float):         rate as a fraction (0.0-1.0)
    """
    rate = 0.0
    for delta in (0.1, 0.01, 0.001, 0.0001):
        while compound_interest(rate+delta, years) <= value:
            rate += delta

    return rate


def main():
    """
    exerciser for these functions
    """

    print("compound interest:")
    for years in (1, 2, 4, 8, 16):
        print(f"\tperiod: {years} years:")
        for rate in (0.01, 0.02, 0.05, 0.075, 0.10):
            result = compound_interest(rate, years)
            inferred = compound_rate(result, years)
            print(f"\t\t{rate*100:5.2f}: {result:7.4f} ({inferred*100:5.2f})")


if __name__ == "__main__":
    main()
