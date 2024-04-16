from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import PyPDF2
import pandas as pd
import json
from html_parser import naming



pdfFileObj = open('/Users/danielkrill/eg-business/couriers/pdf/928.pdf', 'rb')
ROUND_NUM = 8
location = 1

# creating a pdf reader object
pdfReader = PyPDF2.PdfReader(pdfFileObj)


def parse_primary_segments_from_pdf(rd, industry):
    pdfFileObjw = open('couriers/pdf/' + str(industry) +
                      str(rd) + '.pdf', 'rb')
    pdfReaderw = PyPDF2.PdfReader(pdfFileObjw)
    data_dict = {}
    prod_data = pdfReaderw.pages[3].extract_text().split('\n')
    for row in prod_data:
        row = row.split(' ')
        if len(row) < 4:
            continue
        ps = naming(row[1])
        prod = row[0]
        team = prod[0]
        # append prod to data_dict[team][ps] if list exists, else make a new list
        if team in data_dict:
            if ps in data_dict[team]:
                data_dict[team][ps].append(prod)
            else:
                data_dict[team][ps] = [prod]
        else:
            data_dict[team] = {ps: [prod]}
    print(json.dumps(data_dict, indent=4))
    return data_dict

# creating a page object
segments = ["traditional", "low-end", "high-end", "performance", "size"]
all_segment_data = dict(zip(segments, pdfReader.pages[4:9]))
our_products = []
our_segemnts = []
round_no = None
round_ending = None

for segment, page in all_segment_data.items():
    text_lines = page.extract_text().split('\n')
    flag = False
    segment_data = []
    round_no = int(text_lines[1][-1])
    round_ending = text_lines[2] 

    for line in text_lines:
        if line == 'Survey':
            flag = True
            continue
        if flag:
            words = line.split(' ')
            if words[0] == 'CAPSTONE':
                continue
            if not words[4].isalpha():
                words.insert(4, "NO")


            words[3] = int(datetime.strptime(words[3], "%m/%d/%Y").month)
            words.pop(1)
            words.pop(1)
            words.insert(1, ROUND_NUM)
            words.insert(2, segment)

            # Extract the month
            
            segment_data.append([word for word in words if word != ''])

    all_segment_data[segment] = segment_data

pdfFileObj.close()



columns = ['name', 'market share', 'units sold to segment', 'revision date', 'stock out', 'performance', 'size', 'list price', 'mtbf', 'age dec 31', 'promo budget', 'awareness', 'sales budget', 'accessibility', 'dec cust survey']


# Define the scope and credentials
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'sheetskey.json', scope)
client = gspread.authorize(creds)

# Open the spreadsheet by title
spreadsheet = client.open('Forecasting')

# TODO: make constant OR BETTER write directly to csv 
worksheet = spreadsheet.get_worksheet(-1)

#no longer using

for k, segment in all_segment_data.items():
    df = pd.DataFrame(segment, columns=columns)
    # Convert DataFrame to list of lists (for gspread)
    data_to_write = df.values.tolist()

    # Include the DataFrame's header
    # data_to_write.insert(0, df.columns.to_list())

    # worksheet.update(range_name = 'A' + str(location), values=[[k]])
    worksheet.update('A' + str(location), data_to_write)
    location += len(data_to_write)


# for k, v in all_segment_data.items():
#     for l in v:
#         if l[0][0] == 'C':
#             l.insert(1, k)
#             our_products.append(l)
# columns.insert(1, 'segment')
# our_products_df = pd.DataFrame(our_products, columns=columns)
# past_year_df = our_products_df.drop(['segment', 'market share', 'units sold to segment', 'revision date', 'stock out', 'promo budget', 'sales budget'], axis=1)

# our_products_df = our_products_df[['name', 'segment']]
# our_products_df = our_products_df.sort_values(by='name')
# data_to_write = our_products_df.values.tolist()

# worksheet.update(range_name='s2', values=[['Our Products']])
# worksheet.update(range_name='s3', values=data_to_write)
