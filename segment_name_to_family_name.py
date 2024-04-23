import csv
import json

segment_to_family_list = {}
with open('unspsc_taxonomy.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        segment_name = row['Segment Name']
        family_name = row['Family Name']
        if segment_name not in segment_to_family_list:
            segment_to_family_list[segment_name] = set()
        segment_to_family_list[segment_name].add(family_name)

for segment_name in segment_to_family_list:
    segment_to_family_list[segment_name] = list(segment_to_family_list[segment_name])
    
with open('segment_name_to_family_name.json', 'w') as f:
    json.dump(segment_to_family_list, f)
        