from flask import Flask, make_response, jsonify, request
from flask_cors import CORS
import xml.etree.ElementTree as ET
import csv
from bs4 import BeautifulSoup
import html_parser
import os
import json
from functions import *


app = Flask(__name__)
CORS(app)

# def parse_csv(file_path):
#     data_dict = {}
#     current_segment = None
#     current_year = None

#     with open(file_path, 'r') as csvfile:
#         reader = csv.reader(csvfile)

#         for row in reader:
#             if not row:  # Skip empty rows
#                 continue

#             if 'age' in row:  # Header row
#                 headers = row
#             elif len(row) == 1:  # Segment or Year row
#                 if row[0].isdigit():  # Year row
#                     current_year = row[0]
#                 else:  # Segment row
#                     current_segment = row[0]
#                     data_dict[current_segment] = {}
#             else:  # Data row
#                 if current_year not in data_dict[current_segment]:
#                     data_dict[current_segment][current_year] = {
#                         header: [] for header in headers}

#                 for i, value in enumerate(row):
#                     data_dict[current_segment][current_year][headers[i]].append(
#                         float(value))
#     return data_dict

@app.route('/score')
def score(prc=0, seg=0, rvm=0, mto=0, mtn=0, ago=0, szo=0, szn=0, pfo=0, pfn=0, prm=0, awa=0, sal=0, acc=0, arp=0, test=0, rd=0, up=1):
    # get preferences for each segment
    file_path = 'couriers/json_prefs/round' + str(rd) + 'prefs.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            seg_prefs = json.load(file)
    else:
        seg_prefs = html_parser.parse_html_prefs(rd)

    # set params from Google Sheet
    if not test:
        inputs = request.args
        prc = float(inputs['prc'])
        seg = inputs['seg']
        rvm = int(inputs['rvm'])
        mto = int(inputs['mto'])
        mtn = int(inputs['mtn'])
        ago = float(inputs['ago'])
        szo = float(inputs['szo'])
        szn = float(inputs['szn'])
        pfo = float(inputs['pfo'])
        pfn = float(inputs['pfn'])
        prm = float(inputs['prm'])
        awa = float(inputs['awa'])
        acc = float(inputs['acc'])
        sal = float(inputs['sal'])
        arp = float(inputs['arp'])
        rd = int(inputs['rd'])
        up = int(inputs.get('up', 1))

    # get raw scores for each category
    price_score, price_mults = get_price_score(
        prc,
        seg_prefs[seg]['price']['value']
    )
    mtbf_score = get_mtbf_score(
        rvm,
        seg_prefs[seg]['mtbf']['value'],
        mto,
        mtn
    )
    age_score = get_age_score(
        rvm,
        seg_prefs[seg]['age']['value'],
        ago,
        seg,
        up
    )
    position_score, position_mults, iddist = get_position_score(
        rvm,
        seg_prefs[seg]['size']['value'],
        seg_prefs[seg]['pfmn']['value'],
        szo,
        szn,
        pfo,
        pfn,
        seg
    )

    weights = {}
    for attr in seg_prefs[seg]:
        weights[attr] = float(seg_prefs[seg][attr]['importance'])/100
    averages = [100 * position_mult * price_mult * ((price * weights['price'] + mtbf * weights['mtbf'] + age * weights['age'] + position * weights['size'])
                                                    if position > 0 and price > 0 and mtbf > 0 else 0)
                for price, price_mult, mtbf, age, position, position_mult
                in zip(price_score, price_mults, mtbf_score, age_score, position_score, position_mults)]

    # online guide says to weight like this before applying acc/awa, not sure if this is before or after the multipliers
    averages = [(a/10)**2 for a in averages]

    # marketing effects
    awareness = (awa * 2 / 3) + get_awareness_increase(prm)
    accessibility = (acc * 2 / 3) + get_accessibility_increase(sal, 2)
    averages = [(a * pm * pms * (1 + awareness) / 2) *
                (1 + accessibility) / 2 for a, pm, pms in zip(averages, position_mults, price_mults)]
    averages = [a * get_ar_effect(arp) for a in averages]

    # track raw scores for each category
    wscores = []
    for p in price_score:
        wscores.append(p)
    for p in mtbf_score:
        wscores.append(p)
    for p in age_score:
        wscores.append(p)
    for p in position_score:
        wscores.append(p)

    if test:
        return wscores, averages, iddist

    # return xml object for Google Sheet
    data = ET.Element("data")

    if int(inputs.get('brk', 0)):
        for sublist in [price_score, mtbf_score, age_score, position_score]:
            item = ET.SubElement(data, 'Item')
            for i, value in enumerate(sublist):
                # Creating sub-elements for each item in the sublist
                subelement = ET.SubElement(item, f'Field{i+1}')
                subelement.text = str(value)
        xml_data = ET.tostring(data, encoding='unicode')
        response = make_response(xml_data)
        response.headers['Content-Type'] = 'application/xml'
        return response

    for avg in averages:
        item = ET.SubElement(data, "item")
        item.text = str(avg)
    for w in wscores:
        item = ET.SubElement(data, "item")
        item.text = str(w)

    xml_data = ET.tostring(data, encoding='unicode')

    response = make_response(xml_data)
    response.headers['Content-Type'] = 'application/xml'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5040)
