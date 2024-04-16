from functions import *
from forechester import score
from loader import load
from html_parser import parse_primary_segments, parse_html_prefs
from pdf_to_prodlist import parse_primary_segments_from_pdf
# original_str = "$C$34, P14/$C$40 * ($C$35*$C$36^C41) / 12,"

# # Replacements for 'c'
# replacements = ['d', 'e', 'f', 'g']

# # Initialize list to store modified strings
# modified_strings = []

# # Generate new strings with replacements
# for rep in replacements:
#     modified_str = original_str.replace('c', rep)
#     modified_strings.append(modified_str)

# # Print or use the modified strings
# print(original_str, end="")
# for string in modified_strings:
#     print(string, end="")


def unit_test_pos():
    # res, mult = get_position_score(7, 10.2, 9.8, 0, 10.2, 0, 9.8, "high-end")
    res, mult, tv = get_position_score(
        0, 9.3, 10.7, 3, 17, 3, 17,"high-end", 1)
    print("\nUnit Test Data")
    for i, r in enumerate(res):
        print(i + 1, r)
    print(mult)


def unit_test_age():
    res = get_age_score(6, 2.41, "low-end", 1, 1)
    print(res)


def unit_test_marketing():
    print("testing awarenes")
    for i in range(0, 3000, 500):
        print(i, get_awareness_increase(i))

    print("testing access")
    for i in range(0, 3000, 500):
        print(i, get_accessibility_increase(i, 2))


# unit_test_product(name, industry, rd):
#     product = 

#def score(prc=0, seg=0, rvm=0, mto=0, mtn=0, ago=0, szo=0, szn=0, pfo=0, pfn=0, prm=0, awa=0, sal=0, acc=0, arp=0, test=0, rd=0, up=1, new=0, debug=0, run=0):

# print(score(38, "high-end", 5, 0, 22500, 0, 0, 8.4, 0, 11.6, 1000, awa=0, sal=1000, acc=.52, arp=45, test=1, rd=2, up=1, new=1))

params2 = ['name', 'market share', 'units sold to segment', 'revision date', 'stock out', 'performance', 'size',
           'list price', 'mtbf', 'age dec 31', 'promo budget', 'awareness', 'sales budget', 'accessibility', 'dec cust survey']

parse_html_prefs(4, "high-end")