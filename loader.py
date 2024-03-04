




from bs4 import BeautifulSoup
import re
import json
from html_parser import parse_html_prefs
import os
import pandas as pd

def convert_to_float(s):
    if s in {"", "YES"}:
        return 0

    if "/" in s:
        return int(s.split("/")[0])

    cleaned = re.sub(r'[,\$]', '', s)

    # Detect and convert percentages
    if '%' in cleaned:
        cleaned = cleaned.replace('%', '')
        return float(cleaned) / 100
    else:
        return float(cleaned)

def parse_segments(soup, team_letter: str = "A"):
    segments = ["traditional", "low-end", "high-end", "performance", "size"]
    trad = soup.find('a', attrs={"name": "ms1"}).find_all(
        'table')[12].find_all('tr')
    low_e = soup.find('a', attrs={"name": "ms2"}).find_all(
        'table')[12].find_all('tr')
    high = soup.find('a', attrs={"name": "ms3"}).find_all(
        'table')[12].find_all('tr')
    perf = soup.find('a', attrs={"name": "ms4"}).find_all(
        'table')[12].find_all('tr')
    sizee = soup.find('a', attrs={"name": "ms5"}).find_all(
        'table')[12].find_all('tr')

    all_segment_data = {seg: [] for seg in segments}
    our_products = []

    for segment, segment_data in zip(segments, [trad, low_e, high, perf, sizee]):
        for row in segment_data[1:]:
            cells = row.find_all(['td', 'th'])
            row_data = [cell.get_text(strip=True)
                        for cell in cells]
            if row_data:
                all_segment_data[segment].append(row_data)
                if row_data[0][0] == team_letter:
                    our_product = row_data.copy()
                    our_product.insert(1, segment)
                    our_products.append(our_product)

        

    for val in all_segment_data.values():
        for row in val:
            # Ensure row is a mutable type if it's not already (e.g., list)
            for i in range(1, len(row)):
                # Directly update the element in the row
                row[i] = convert_to_float(row[i])
    
    return all_segment_data, our_products

def seg_order(segment: str):
    return {
        "traditional": "1",
        "low-end": "2",
        "high-end": "3",
        "performance": "4",
        "size": "5"
    }[segment]


def load_market_data(soup, segment: str = ""):
    market_data = soup.find('a', attrs={"name": "ms" + seg_order(segment)}).find_all(
        'table')[4].find_all('td')
    demand = convert_to_float(market_data[2].get_text(strip=True))
    growth_rate = convert_to_float(market_data[8].get_text(strip=True))
    return demand, growth_rate


def load(round_no: int = 0, segment: str = "", team_letter: str = ""):
    file_path = 'couriers/json_prefs/round' + str(round_no) + 'prefs.json'
    if os.path.exists(file_path):
        with open('couriers/html/round' + str(round_no) + '.html', 'r', encoding="UTF-8") as file:
            html_content = file.read()
    else:
        return {}, {}, 0, 0
    soup = BeautifulSoup(html_content, 'html.parser')

    front_page = soup.find('a', attrs={'name': 'frontpage'}).find_all('td')[
        2].find('b')
    round_no, round_ending = [text for text in front_page.stripped_strings]
    round_no = int(round_no.split()[1])


    segment_df, our_products = parse_segments(soup, team_letter)


    # load preferences
    # TODO load from html courier itself
    seg_prefs = None
    file_path = 'couriers/json_prefs/round' + str(round_no) + 'prefs.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            seg_prefs = json.load(file)
    else:
        seg_prefs = parse_html_prefs(round_no, segment)
    
    demand, growth_rate = load_market_data(soup, segment)


    return segment_df[segment], seg_prefs[segment], demand, growth_rate
