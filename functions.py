import math
from matplotlib import pyplot as plt
from matplotlib.patches import Circle
import numpy as np

def get_price_score(p: float, prefs: list):
    low = prefs['low'] - .5
    high = prefs['high'] - .5
    p_score = 0

    def demand(x: float):
        return .07 * (x - high) ** 2 + 5

    mult = 1

    if p < low - 5 or p > high + 5:
        p_score = 0
    elif p < low:
        p_score = 2 * (p - low) + demand(low)
        mult = 1 - ((low - p) / 5)
    elif low <= p <= high:
        p_score = demand(p)
    elif high < p:
        p_score = high + 5 - p
        mult = 1 - ((p - high) / 5)

    p_score /= demand(low)

    if p_score < 0:
        p_score = 0
    return 12 * [p_score], 12 * [mult]


def get_position_score(revision_month: int, size_pref: float, pfmn_pref: float, old_size: float, new_size: float, old_pfmn: float, new_pfmn: float, seg: str, test=0):
    def distance(p, q):
        return abs(np.linalg.norm(np.array(p) - np.array(q)))

    def round_to_nearest_half(number):
        return round(number * 2) / 2
    scores = []
    mults = []
    iddist = 0

    drifts = {
        'ideal':
        {
            'traditional': {
                'size': 0.0,
                'pfmn': 0.0
            },
            'low-end': {
                'pfmn': -.8,
                'size': .8
            },
            'high-end': {
                'pfmn': 1.4,
                'size': -1.4
            },
            'performance': {
                'pfmn': 1.4,
                'size': -1
            },
            'size': {
                'pfmn': 1,
                'size': -1.4
            }
        },
        'center':
        {
            'traditional': {
                'pfmn': .7,
                'size': -.7
            },
            'low-end': {
                'pfmn': .5,
                'size': -.5
            },
            'high-end': {
                'pfmn': .9,
                'size': -.9
            },
            'performance': {
                'pfmn': 1.0,
                'size': -.7
            },
            'size': {
                'pfmn': .7,
                'size': -1.0
            }
        }
    }
    rads = {
        'traditional': [
            0, .4, .6, .8, 1.1, 1.3, 1.55, 1.85, 2.15, 2.6
        ], 
        'low-end': [
            0, .6, .9, 1.2, 1.4, 1.7, 1.9, 2.2, 2.8, 3.7
        ],
        'high-end': [
            0, 1, 1.4, 1.8, 2.1, 2.5, 2.9, 3.4, 4.1, 4.7
        ],
        'performance': [
            0, 1, 1.4, 1.8, 2.1, 2.5, 2.9, 3.4, 4.1, 4.7
        ],
        'size': [
            0, 1, 1.4, 1.8, 2.1, 2.5, 2.9, 3.4, 4.1, 4.7
        ]
    }

    # our product - updates at most once during year
    curr_product = np.array([old_pfmn, old_size])
    ideal_pfmn = pfmn_pref * 1.00000
    ideal_size = size_pref * 1.00000
    # TODO: see if is calculated in middle of month or end of month
    curr_pfmn = ideal_pfmn - drifts['ideal'][seg]['pfmn'] 
    curr_size = ideal_size - drifts['ideal'][seg]['size'] 

    mult = 1
    for_plot = [[13, curr_product]]
    centers = []

    def base_performance(curr_product, segment_center):
        dist_to_center = distance(segment_center, curr_product)
        score, mult = 0, 1
        if round_to_nearest_half(dist_to_center) >= 4:
            score = 0
        # between rough and fine (orange)
        elif dist_to_center >= 2.5:
            score = ((4 - dist_to_center) / 1.5) * .1  # rought weighting
            mult = score / .1
        # in fine cut
        else:
            segment_ideal = np.array(
                [curr_pfmn + drifts['ideal'][seg]['pfmn'], curr_size + drifts['ideal'][seg]['size']])
            dist_to_ideal = distance(segment_ideal, curr_product)

            def get_score_from_distance_to_ideal(dist_to_ideal, rads):
                for index, rad in enumerate(rads):
                    if dist_to_ideal < rad:
                        return (rad - dist_to_ideal) / (rad - rads[index-1]) * .1 + .1 * (len(rads) - index)
            score = get_score_from_distance_to_ideal(dist_to_ideal, rads[seg])
        return score, mult

    for i in range(1, 13):
        # update product
        if i == revision_month:
            curr_product = np.array([new_pfmn, new_size])
            for_plot.append([i+12, curr_product])

        # calculate new monthly centers
        curr_pfmn += drifts['center'][seg]['pfmn'] / 12
        curr_size += drifts['center'][seg]['size'] / 12
        segment_center = np.array([curr_pfmn, curr_size])

        score, mult = base_performance(curr_product, segment_center)

        centers.append([i, segment_center])
        scores.append(score)
        mults.append(mult)


    if test:
        test_scores = []
        plt.plot([curr_pfmn], [curr_size], 'ro')

        x = np.arange(int(curr_pfmn - 5), int(curr_pfmn + 6), .0625)
        y = np.arange(int(curr_size - 5), int(curr_size + 6), .0625)
        to_graph = []
        for ex in x:
            for why in y:
                test_scores.append(base_performance( [ex, why],
                    [curr_pfmn, curr_size])[0])
                to_graph.append([ex, why])
                # if test_scores[-1] > .75:
                #     print(ex, why, test_scores[-1])
        plt.scatter([a[0] for a in to_graph], [a[1] for a in to_graph], c=test_scores, cmap='viridis', s=10)
        plt.title('Base Performance with center at {} (December 31)'.format([curr_pfmn, curr_size]))
        plt.show()
        exit()

    # graph for visual debugging
    if test:
        fig, ax = plt.subplots()
        for pair in centers:
            month, point = pair
            ax.plot(point[0], point[1], marker='o', markersize=5)

            ax.text(point[0], point[1], f'{month}', fontsize=9, ha='right')
            circle = Circle(point, 2.5, color='red', fill=False)
            if month == 12:
                ax.add_patch(circle)

        for pair in for_plot:
            month, point = pair
            print(month, point)
            size = 5
            if month > 12:
                size = 9
            ax.plot(point[0], point[1], marker='x',
                    markersize=size, color="black", )

            ax.text(point[0]-.1, point[1],
                    f'{month%12} | {round(scores[month%12-1], 3)}', fontsize=9, ha='right')

        ax.set_xlabel('Performance')
        ax.set_ylabel('Size')
        ax.set_title(seg)
        fig.show()

    return scores, mults

def get_mtbf_score(revision_month: int, prefs: list, old_mtbf: int, new_mtbf: int):
    low = prefs['low']
    high = prefs['high']

    # voodoo?? needs fixing bc performance is the least consistently inaccurate - is it just linear?
    def base_mtbf(x: float):
        if x < low - 5000:
            return 0
        elif x < low:
            return (x - (low - 5000)) / (low - (low - 5000))* .1
        elif x >= high:
            return 1
        else:
            return (x - low) / (high - low) * .9 + .1
            #return (.28 * (x/1000 - (low/1000 - 1)) ** 2) / 10

    # def base_mtbf(mtbf):
    #     temp = (mtbf - low) / (high - low)
    #     if temp < 0 : temp = 0
    #     if temp > 1 : temp = 1
    #     return temp

    # x = np.arange(low-5000, high+1000, 1000)
    # y = [base_mtbf(i) for i in x]
    # plt.plot(x, y)
    # plt.show()


    scores = []
    score = 0
    for i in range(1, 13):
        if i < revision_month:
            score = base_mtbf(old_mtbf)
        elif i == revision_month:
            score = (base_mtbf(old_mtbf) + base_mtbf(new_mtbf)) / 2
        elif i > revision_month:
            score = base_mtbf(new_mtbf)
        scores.append(score)
    return scores


def get_age_score(revision_month: int, old_age: float, seg: str, update: int, test: int = 0, new_product: bool = False, debug: int=0):
    equation_params = {
        'low-end': {
            'center': 7,
            'spread': 7.5
        },
        'high-end': {
            'center': 0,
            'spread': 3
        },
        'traditional': {
            'center': 2,
            'spread': 3.6
        },
        'size': {
            'center': 1.5,
            'spread': 3.2
        },
        'performance': {
            'center': 1,
            'spread': 1.6
        }
    }

    # bell curve around center with stdev of spread
    def base_age(age):
        res = math.exp(-(age - equation_params[seg]['center'])
                       ** 2 / equation_params[seg]['spread'] * 1.5)
        if age < equation_params[seg]['center'] - equation_params[seg]['spread'] / 2 or age > equation_params[seg]['center'] + equation_params[seg]['spread'] / 2:
            res *= .4
        return res
    
    # if debug:
    #     # make scatter graph with x as range from 0 to 7 with step .25 and y as base_age(x)
    #     x = np.arange(0, 10, .125)
    #     y = [base_age(i) for i in x]
    #     plt.plot(x, y)
    #     plt.show()


    scores = []
    score = 0

    # assume old_age (listed on courier) is the age for december of last year
    current_age = old_age
    for i in range(1, 13):
        if debug:
            print(current_age)
        current_age += (1/12)
        if i == revision_month and update:
            if new_product:
                current_age = 0
            else:
                current_age /= 2
        score = base_age(current_age)
        scores.append(score)
    return scores

def get_awareness_increase(budget: float, new: bool = False):
    def f(x, a, c, b, d):
        return a + (c - a) * np.exp(-1 * np.exp(b * (x - d)))

    if budget < 0:
        return .25
    
    extra_pct = f(budget/100, -1.4, 49.2, -.16, 8.3) / 100

    if new:
        extra_pct += .25
    return extra_pct

def get_accessibility_increase(budget: float, num_products: int):
    if budget >= 3000 and num_products == 1:
        return .31

    def f(x, a, c, k):
        return (c / (1 + a * np.exp(-k * (x - 2)))) - 0.25

    if budget < 0:
        return .25
    extra_pct = f(budget/1000, .67, 3.87, 1.47) / 10
    if extra_pct < 0:
        extra_pct = 0
    return extra_pct

def get_ar_effect(days: float):
    if days <= 10:
        return .6
    elif days <= 30:
        return .93
    elif days <= 45:
        return .95
    elif days <= 60:
        return .993
    else:
        return 1

def is_in_rough_cut(seg: str, prc: float, pfmn: float, size: float):
    return seg in ['low-end', 'high-end', 'traditional']