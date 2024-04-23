import csv
import sys
import json

def read_csv(file_path):

    data = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            data.append(row)

    return data

def count_words(data):
    word_count = {}
    for row in data:
        url = row['url']
        url_split = url.split('/')
        for word in url_split:
            word_split = word.split('-')
            for w in word_split:
                w = w.lower()
                if w in word_count:
                    word_count[w] += 1
                else:
                    word_count[w] = 1

        href_text = row['href_text']
        href_text_split = href_text.split(' ')

        for word in href_text_split:
            word = word.lower()
            if word in word_count:
                word_count[word] += 1
            else:
                word_count[word] = 1

        # print word count descending
        word_count = dict(sorted(word_count.items(), key=lambda item: item[1], reverse=True))

        with open('word_count.json', 'w') as file:
            json.dump(word_count, file)


def read_unspsc_csv(file_path):
    data = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            data.append(row)
    return data

# if __name__ == "__main__":
#     file_path = sys.argv[1]
#     data = read_csv(file_path)

#     print("Column names: %s" % ", ".join(data[0].keys()))
#     rows_with_not_null_href = [row for row in data if row['href_text'] != '']

#     with open('rows_with_not_null_href.csv', 'w') as file:
#         writer = csv.DictWriter(file, fieldnames=data[0].keys())
#         writer.writeheader()

#         for row in rows_with_not_null_href:
#             writer.writerow(row)

#     count_words(data)

#     unspc_dict = {}
#     family_names = 0

#     data = read_unspsc_csv(file_path)
#     for row in data:
#         family_name = row['Family Name']
#         commodity_name = row['Commodity Name']

#         if family_name not in unspc_dict:
#             family_names += 1
#             unspc_dict[family_name] = set()
#         unspc_dict[family_name].add(commodity_name)
    
#     unspc_dict = {k: list(v) for k, v in unspc_dict.items()}

#     print(family_names)

#     with open('unspc.json', 'w') as file:
#         json.dump(unspc_dict, file)

if __name__ == "__main__":
    return
