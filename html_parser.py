from bs4 import BeautifulSoup
import re
import json

def naming(attr):
    if attr == 'Reliability':
        return 'mtbf'
    elif attr == 'Ideal Position':
        return 'position'
    elif attr == 'Price':
        return 'price'
    elif attr == 'Age':
        return 'age'
    return None

def parse_html_prefs(rd):
    print("Parsing Segments from HTML...")
    data_dicts = []  # List to store all dictionaries from each table
    with open('pround'+str(rd)+'.html', 'r', encoding="UTF-8") as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')

    centers = soup.find_all('center')
    for center in centers:
        if 'Customer Buying Criteria' in center.get_text():
            table = center.find_parent('table')

            if table:
                rows = table.find_all('tr')[2:]  # Skipping header rows
                data_dict = {}
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 4:  # Ensure there are enough cells
                        attribute = cells[1].get_text(strip=True)
                      
                        if naming(attribute) == 'position':
                            #add two elements
                            vals = cells[2].get_text(strip=True).split()
                            importance = float(
                                cells[3].get_text(strip=True)[:-1])
                            data_dict['size'] = {
                                'value': float(vals[3]), 'importance': importance}
                            data_dict['pfmn'] = {
                                'value': float(vals[1]), 'importance': importance}
                            continue

                        elif naming(attribute) == 'mtbf':
                            value = [int(num) for num in re.findall(
                            r'\d+', cells[2].get_text(strip=True))]
                        elif naming(attribute) == 'price':
                            value = [float(num) for num in re.findall(
                                r'\d+\.\d+', cells[2].get_text(strip=True))]
                        elif naming(attribute) == 'age':
                            value = 2 * [float(num) for num in re.findall(
                                r'\d+\.\d+', cells[2].get_text(strip=True))]
                        value = dict(zip(['low', 'high'], value))
                        importance = float(
                            cells[3].get_text(strip=True)[:-1])

                        data_dict[naming(attribute)] = {
                            'value': value, 'importance': importance}

                data_dicts.append(data_dict)

    
    segments = ['traditional', 'low-end', 'high-end', 'performance', 'size']
    res = dict(zip(segments, data_dicts))
    print("Finished Parsing Segments from HTML!")

        # Writing the dictionary to a JSON file
    file_path = 'couriers/json_prefs/round'+str(rd)+'prefs.json'  # Adjust the file path as needed
    with open(file_path, 'w') as file:
        json.dump(res, file)

    return res