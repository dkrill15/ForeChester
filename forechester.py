from flask import Flask, make_response
from flask_cors import CORS
import xml.etree.ElementTree as ET
import html_parser
import os
import json
from functions import *

app = Flask(__name__)
CORS(app)

def make_xml_response(avgs, wscores):
    data = ET.Element("data")
    for avg in avgs:
        item = ET.SubElement(data, "item")
        item.text = str(avg)
    for w in wscores:
        item = ET.SubElement(data, "item")
        item.text = str(w)

    xml_data = ET.tostring(data, encoding='unicode')

    response = make_response(xml_data)
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/score')
def score(prc=0, seg=0, rvm=0, mto=0, mtn=0, ago=0, szo=0, szn=0, pfo=0, pfn=0, prm=0, awa=0, sal=0, acc=0, arp=45, test=0, rd=0, up=1, new=0, debug=0):
    # get preferences for each segment
    file_path = 'couriers/json_prefs/round' + str(rd) + 'prefs.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            seg_prefs = json.load(file)
    else:
        seg_prefs = html_parser.parse_html_prefs(rd, seg)

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
        ago,
        seg,
        up,
        test,
        new,
        debug
    )
    position_score, position_mults = get_position_score(
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

    # if debug:
    #     print("Averages before marketing effects",
    #           [round(a, 0) for a in averages])

    # marketing effects
    awareness = (awa * 2 / 3) + get_awareness_increase(prm, awa == 0)
    accessibility = (acc * 2 / 3) + get_accessibility_increase(sal, 2)
    averages = [(a * pm * pms * (1 + awareness) / 2) *
                (1 + accessibility) / 2 for a, pm, pms in zip(averages, position_mults, price_mults)]
    averages = [a * get_ar_effect(arp) for a in averages]

    if debug:
        print(awareness, accessibility)
        # print("Averages after marketing effects", [round(a, 0) for a in averages])


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
        return wscores, averages, 0, awareness, accessibility
    # if debug:
    #     print(wscores)
    return averages

if __name__ == '__main__':
    app.run(debug=True, port=5040)
