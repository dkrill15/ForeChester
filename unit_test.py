from functions import *

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
        3, 9.6, 4.7, 10, 10.2, 4, 4.2, "size", 1)
    print("\nUnit Test Data")
    for i, r in enumerate(res):
        print(i + 1, r)
    print(mult)


def unit_test_age():
    res = get_age_score(6, 2, 2.41, "traditional", 1)
    print(res)


def unit_test_marketing():
    print("testing awarenes")
    for i in range(0, 3000, 500):
        print(i, get_awareness_increase(i))

    print("testing access")
    for i in range(0, 3000, 500):
        print(i, get_accessibility_increase(i, 2))


unit_test_age()
