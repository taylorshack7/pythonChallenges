def number_pattern(n):
    range_count = ''
    if not(n.type(int)):
        return ("Argument must be an integer value.")
    elif n < 1:
        return ("Argument must be an integer greater than 0.")
    for x in range(1, n):
        range_count.append(x + ' ')
    return (range_count)
number_pattern(4)