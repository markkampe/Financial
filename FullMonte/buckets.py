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
    for result in results:
        if result > max_result:
            max_result = result

    # try pick a size that results in reasonable number of buckets
    width = 1.0
    while max_result/width < 10:
        width /= 10

    if max_result/width < 25:
        return width/4
    if max_result/width < 50:
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
    for result in results:
        if result > max_result:
            max_result = result
    num_buckets = int((max_result + granularity)/granularity)
    buckets = [0] * (num_buckets)

    # compute the count for each bucket
    for result in results:
        bucket = int(result/granularity)
        buckets[bucket] += 1

    return buckets


# pylint: disable=consider-using-enumerate
def distribution(buckets, granularity):
    """
    turn a list of count buckets into scatter-plot points
    :param buckets [int ...]: list of count buckets
    :param granularity (float): x-width of each bucket
    :param cut_off (int): counts below this are not shown
    :return ([x-values], [y-percentage-values])
    """
    # get total number of counts
    total = 0
    for i in range(len(buckets)):
        total += buckets[i]

    x_values = []
    y_values = []
    for i in range(len(buckets)):
        pct = buckets[i] * 100 // total
        if pct > 0:
            x_values.append(i * granularity)
            y_values.append(pct)

    return (x_values, y_values)
