
import csv
import forechester
import pandas as pd
import matplotlib.pyplot as plt
import html_parser
import sys
import os
import mpld3
from mpld3 import plugins
import json
from html_parser import parse_primary_segments
from pdf_to_prodlist import parse_primary_segments_from_pdf


if len(sys.argv) < 3:
    print("ERROR | Enter both an industry and the index of the product for which you want a fine-grained analysis (-1 if not needed).")
    exit()

industry = sys.argv[1]
TO_CHECK = int(sys.argv[2])

fp = 'test_data/' + industry + '.csv'
if not os.path.exists(fp):
    print(f"ERROR | Industry {industry} is not a valid industry. Try from the list below:")
    for f in os.listdir('test_data'):
        print('\t' + f[:-4])
    exit()

df = pd.read_csv(fp)
df.columns = ['name', 'round', 'segment', 'revision date', 'stock out', 'performance', 'size', 'list price',
              'mtbf', 'age dec 31', 'promo budget', 'awareness', 'sales budget', 'accessibility', 'dec cust survey']

if TO_CHECK not in df.index and TO_CHECK != -1:
    print(f"ERROR | Index {TO_CHECK} does not match a product in this industry.")
    exit()

# Initialize 'Forecast' column to 0
df['Forecast'] = 0
df = df.drop(['stock out'], axis=1)

# Filter rows where 'round' > 0 once, to avoid doing it inside the loop
preds = df[df['round'] > 0].copy()

# Pre-calculate and store data to avoid repetitive filtering
previous_round_info = {}
for name, group in df.groupby('name'):
    for tround in group['round'].unique():
        prev_round_df = group[group['round'] == tround - 1]
        if not prev_round_df.empty:
            previous_round_info[(name, tround)] = prev_round_df.iloc[0]

examine = []
examine_row = None
examine_param = None

# TODO make this reflect primary segments as listed in the production page
primary_segments = { rd : parse_primary_segments_from_pdf(rd, industry) for rd in range(1, df['round'].max() + 1) }
print(json.dumps(primary_segments, indent=4))
accessibility_budgets = {
    rd : { 
        seg : {
            let: df[(df['name'].astype(str).isin(primary_segments[rd][let].get(seg, []))) & (df['round'] == rd) & (df['segment'] == seg)]['sales budget'].sum() for let in ['A', 'B', 'C', 'D', 'E', 'F']
            } for seg in ['high-end', 'low-end', 'traditional', 'performance', 'size']
        } for rd in range(1, df['round'].max() + 1)
}

# print json object formatted
print(json.dumps(accessibility_budgets, indent=4))

# Iterate over the filtered DataFrame
for i, row in preds.iterrows():
    key = (row['name'], row['round'])


    if key in previous_round_info:
        o = previous_round_info[key]
        
        ## LOGIC FOR MTBF CHANGES NOT AFFECTING AGE
        update_age = 1
        if o['performance'] == row['performance'] and o['size'] == row['size']:
            update_age = 0

        send = [
            float(row['list price']), 
            row['segment'], 
            float(row['revision date']),
            float(o['mtbf']), float(row['mtbf']), float(o['age dec 31']),
            float(o['size']), float(row['size']), float(o['performance']),
            float(row['performance']),
            float(row['promo budget']), float(o['awareness']),
            accessibility_budgets[row['round']][row['segment']][row['name'][0]], 
            float(o['accessibility']), 
            45, 1, int(row['round']) - 1, update_age, 0
        ]
    elif row['round'] > 0:
        #new product
        print(accessibility_budgets[row['round']]
              [row['segment']][row['name'][0]])
        send = [
            float(row['list price']), 
            row['segment'], 
            float(row['revision date']),
            0, float(row['mtbf']), 0,
            0, float(row['size']), 0,
            float(row['performance']),
            float(row['promo budget']), 0,
            accessibility_budgets[row['round']][row['segment']][row['name'][0]], 
            preds[(preds['round'] == row['round'] - 1) & (preds['name'].astype(str).str[0] == row['name'][0]) & (preds['segment'] == row['segment'])]['accessibility'].mean(), 
            45, 1, int(row['round']) - 1, 1, 1
            ]

    else:
        continue

    if row['name'] == 'Cid':
        print(send)

    wscores, averages, test_val, awareness, accessibility = forechester.score(*send)

    preds.at[i, 'Forecast'] = round(averages[11], 0)
    preds.at[i, 'Test Val'] = round(test_val, 2) 
    # actual - predicted
    preds.at[i, 'awa_diff'] = preds.at[i, 'awareness'] - round(awareness, 2)
    preds.at[i, 'acc_diff'] = preds.at[i, 'accessibility'] - round(accessibility, 2)

    if i == TO_CHECK:
        examine = [wscores[i:i + 12]
                    for i in range(0, len(wscores), 12)]
        examine_row = row
        examine_param = send
        forechester.score(*send, 1)

if industry == '92':
    preds.at[150, 'Forecast'] = 0

# add diffs column
preds['diffs'] = preds['dec cust survey'] - preds['Forecast']
preds['diffs'] = preds['diffs'].abs()

preds = preds.sort_values(by=['segment', 'diffs'], ascending=[True, False])
with pd.option_context('display.max_rows', None,
                       'display.max_columns', None,
                       'display.precision', 3,
                       ):
    print(preds.to_string())
    spdf = pd.DataFrame(examine, index=['price', 'mtbf', 'age', 'position'])
    print(spdf.to_string())
    print(examine_row)

fig, ax = plt.subplots(figsize=(15, 5))
ax.set_title(('Performance of ForeChester for Industry ' + industry + '; MAE = ' + str(preds[(preds['dec cust survey'] != 0) | (preds['Forecast'] != 0)]['diffs'].mean())))
ax.set_ylabel(ylabel=('Customer Survey Score'), fontsize=15)
ax.set_xlabel(('Product Index, Grouped By Segment (high-end, low-end, performance, size, traditional)'), fontsize=15)

actuals, = ax.plot([x + 1 for x in range(0, len(preds))], preds['dec cust survey'], marker='o',
         linestyle='-', color='blue', label='Actual Score', markersize=10)
predictions, = ax.plot([x + 1 for x in range(0, len(preds))], preds['Forecast'], marker='o',
         linestyle='--', color='red', label='ForeChester Prediction', markersize=10)

preds['diffs'] = preds['dec cust survey'] - preds['Forecast']

ax.grid(True)
ax.legend()

# tooltip_a = plugins.PointLabelTooltip(actuals, labels=[str(name) + "'s score in " + seg + " at the end of round " + str(rd) for name, seg, rd in zip(preds['name'], preds['segment'], preds['round'])])
# tooltip_p = plugins.PointLabelTooltip(predictions, labels=[str(name) + "'s score in " + seg + " at the end of round " + str(rd) for name, seg, rd in zip(preds['name'], preds['segment'], preds['round'])])
tooltip_a = plugins.PointLabelTooltip(actuals, labels=[str(i) + preds.loc[i, 'name'] + str(preds.loc[i, 'round']) for i in preds.index])
tooltip_p = plugins.PointLabelTooltip(predictions, labels=[str(
    i) + preds.loc[i, 'name'] + str(preds.loc[i, 'round']) for i in preds.index])


    

plugins.connect(fig, tooltip_a)
plugins.connect(fig, tooltip_p)

# # plot graph where x = preds[acc_diff] and y= preds[diffs]
# fig, ax = plt.subplots(figsize=(15, 5))
# ax.set_title(('Performance of ForeChester for Industry ' + industry + '; MAE = ' + str(preds[(preds['dec cust survey'] != 0) | (preds['Forecast'] != 0)]['diffs'].mean())))
# ax.set_ylabel(ylabel=('Customer Survey Score'), fontsize=15)
# ax.set_xlabel(('Accessibility Difference'), fontsize=15)

# #show the graph
# ax.scatter(preds['acc_diff'], preds['diffs'], color='blue', label='Actual Score', s=100)


mpld3.save_html(fig, "accuracy_graph.html")
