import csv
import json

file_path = 'unspsc_taxonomy.csv'

# all_dict = {}


# with open(file_path, 'r') as file:
#     reader = csv.DictReader(file)
#     for row in reader:
#         segment = row['Segment Name']
#         family = row['Family Name']

#         if segment not in all_dict:
#             all_dict[segment] = set()
#         all_dict[segment].add(family)

#     all_dict = {k: list(v) for k, v in all_dict.items()}
#     with open('segment_to_family.json', 'w') as file:
#         json.dump(all_dict, file)

# get unique segments

with open(file_path, 'r') as file:
    reader = csv.DictReader(file)
    unique_segments = set()
    for row in reader:
        segment = row['Segment Name']
        unique_segments.add(segment)

with open('unique_segments.txt', 'w') as file:
    for segment in unique_segments:
        file.write(segment + '\n')

# json.dump(english_domains, open('english_domains.json', 'w'))
