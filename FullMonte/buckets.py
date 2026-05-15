"""
These methods turn lists of results into distributions for plotting
"""


def bucketwidth(results):
    """
    determine a good bucket width for a set of performance results
    :param [(float)]: simulation results
    :return (float): suggested bucket width
    """
    max_result = 0.0
    min_result = 666.666
    for result in results:
        if result > max_result:
            max_result = result
        if result < min_result:
            min_result = result

    # try pick a size that results in reasonable number of buckets
    data_range = max_result - min_result
    width = 1.0
    while data_range/width < 10:
        width /= 10

    if data_range/width < 25:
        return width/4
    if data_range/width < 50:
        return width/2
    return width


def bucketize(results, granularity):
    """
    turn a list of results into buckets and counts
    :param [(float)]: simulation results
    :param (int): desired bucket width
    :return [(int)] list of bucket counts
    """
    # figure out how many buckets we need
    max_result = 0.0
    min_result = 666.666
    for result in results:
        if result > max_result:
            max_result = result
        if result < min_result:
            min_result = result

    data_range = max_result - min_result
    num_buckets = int((data_range + granularity)/granularity)
    buckets = [0] * (num_buckets)

    # compute the count for each bucket
    for result in results:
        bucket = int((result-min_result)/granularity)
        buckets[bucket] += 1

    return buckets


def value_offset(results):
    """
    find the difference between the lowest sample value and zero
    :param [(float)]: simulation results
    :return (float) lowest sample value
    """
    min_result = 666.666
    for result in results:
        if result < min_result:
            min_result = result
    return min_result


def distribution(buckets, granularity, offset):
    """
    turn a list of count buckets into scatter-plot points
    :param buckets [int ...]: list of count buckets
    :param granularity (float): x-width of each bucket
    :param offset (float): sample value of bucket[0]
           indices are >=0, but samples could be large or negative
    :param cut_off (int): counts below this are not shown
    :return ([x-values], [y-percentage-values])
    """
    # get total number of counts
    total = 0
    for i, count in enumerate(buckets):
        total += count

    x_values = []
    y_values = []
    for i, count in enumerate(buckets):
        pct = count * 100 // total
        if pct > 0:
            x_values.append((i * granularity) + offset)
            y_values.append(pct)

    return (x_values, y_values)
