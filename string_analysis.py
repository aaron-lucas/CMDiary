from collections import Counter, OrderedDict
from math import e, sqrt, floor

def match_chars(test_str, standard):
    """
    Compare the characters in two strings.

    This functon runs through each character in `test_str` and records how many times it occurs in `standard`

    :param test_str:            A string to compare
    :param standard:            A string to compare against
    :return: A ratio between 0 and 1 indicating how many of the characters in `test_str` are in `standard`
    """
    chars_matched = 0
    test_str = ''.join(set(test_str))
    char_counter = Counter(standard)
    for char in test_str:
        match = char_counter.get(char)
        chars_matched += match if match is not None else 0
    return chars_matched/len(standard)


def match_char_for_char(test_str, standard):
    chars_matched = 0
    test_counter = Counter(test_str)
    std_counter = Counter(standard)
    test_chars = ''.join(set(test_str))
    for char in test_chars:
        test_count = test_counter.get(char)
        std_count = std_counter.get(char)
        if None in (test_count, std_count):
            continue
        if test_count > std_count:
            chars_matched += std_count
        else:
            chars_matched += test_count
    return chars_matched / (chars_matched + 1)

def extra_chars(test_str, standard):
    """
    Returns a function of the number of characters which are in test_str but not in standard such that a lower
    number of extra characters will have a greater significance
    """
    for char in standard:
        if char in test_str:
            test_str = test_str.replace(char, '', 1)
    extra = len(test_str)
    return 1/sqrt(extra + 1)

def string_length_ratio(test_str, standard):
    """
    Returns a function of the ratio of the lengths of the two strings (test_str : standard) such that a ratio closer to
    1 will have a greater significance
    """

    ratio = len(test_str)/len(standard)
    return e**0.5 * ratio * e**(-0.5*ratio**2)

def median(values):
    n = len(values)
    pos = floor(n/2)
    if n % 2 == 0:
        median = (values[pos-1] + values[pos]) / 2
    else:
        median = values[pos]

    if not median:
        median = min(values, key=lambda x: x !=0, default=1)
    return median


def get_best_match(test_str):
    commands = ('add', 'remove', 'edit', 'priority', 'extend', 'list', 'filter', 'quit', 'help')

    match_char_results = OrderedDict(sorted({standard: match_chars(test_str, standard) for standard in commands}.items(),
                                     key=lambda t: t[1]))
    match_char_for_results = OrderedDict(sorted({standard: match_char_for_char(test_str, standard) for standard in commands}.items(),
                                         key=lambda t: t[1]))
    extra_char_results = OrderedDict(sorted({standard: extra_chars(test_str, standard) for standard in commands}.items(),
                                     key=lambda t: t[1]))
    string_length_results = OrderedDict(sorted({standard: string_length_ratio(test_str, standard) for standard in commands}.items(),
                                        key=lambda t: t[1]))

    all_results = (match_char_results, match_char_for_results, extra_char_results, string_length_results)
    medians = [median(list(result_set.values())) for result_set in all_results]
    results = {cmd: 0.0 for cmd in commands}

    for index, result_set in enumerate(all_results):
        #print('*****')
        for item in result_set.items():
            #print("{}: {}".format(item[0], item[1]))
            name, value = item
            results[name] += value/medians[index]

    results = OrderedDict(sorted(results.items(), key=lambda t: t[1], reverse=True))
    return max(results, key=lambda x: results[x])

    # print('* * * * *')
    # for item in results.items():
    #     print("{}: {}".format(item[0], item[1]))
    # print('Best Match: {}'.format(max(results, key=lambda x: results[x])))

get_best_match(input('String Analysis > '))