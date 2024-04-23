import csv
csv_file = 'unspsc_taxonomy.csv'

def get_uniques_segment(csv_file):
    data = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    
    uniques = set()
    for row in data:
        family_name = row['Family Name']
        uniques.add(family_name)
    
    return uniques

with open('uniques_segment.txt', 'w') as file:
    for segment in get_uniques_segment(csv_file):
        file.write(f"{segment}\n")

