from sklearn.cluster import KMeans
import numpy as np
import spacy
import json
import csv

# Load a large model to get good word vectors
nlp = spacy.load('en_core_web_lg')

# Load additional data structures
with open('family_to_example_list_20_entry.json', 'r') as f:
    family_to_example = json.load(f)
with open('example_to_family_list_20_entry.json', 'r') as f:
    example_to_family = json.load(f)

# Initialize lists and dictionaries
all_words = list(example_to_family.keys())  # Starting with predefined words
word_list = [word for word in all_words if nlp.vocab.has_vector(word)]


all_products = []
# Read additional words from a text file
with open('output.txt', 'r') as file:
    for line in file:
        all_products.append(line.strip())
        for word in line.strip().split():
            if word not in all_words:
                all_words.append(word)
                if nlp.vocab.has_vector(word):
                    word_list.append(word)

# Prepare word vectors
word_vectors = [nlp(word).vector for word in word_list]

# Set number of clusters
num_clusters = min(len(word_vectors), 100)

# Perform K-means clustering
if len(word_vectors) >= num_clusters and num_clusters > 0:
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(word_vectors)
    labels = kmeans.labels_

    # Organizing words into clusters
    clusters = {}
    for i in range(num_clusters):
        clusters[f"Cluster {i}"] = [word_list[j] for j in range(len(word_list)) if labels[j] == i]

    # Save to JSON
    with open('clusters.json', 'w', encoding='utf-8') as f:
        json.dump(clusters, f, ensure_ascii=False, indent=4)

    # Save to CSV
    with open('clusters.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Cluster Index', 'Words'])
        for i in range(num_clusters):
            words_in_cluster = ", ".join(clusters[f"Cluster {i}"])
            writer.writerow([f"Cluster {i}", words_in_cluster])
else:
    print("Not enough word vectors to perform clustering or the number of clusters is set to zero.")

clusters = {}
with open('clusters.csv', 'r') as f:
    reader = csv.reader(f)
    
    for row in reader:
        if row[0] != 'Cluster Index':
            clusters[row[0]] = row[1].split(', ')

# print(clusters)

segment_name_to_family_name = {}
with open('segment_name_to_family_name.json', 'r') as f:
    segment_name_to_family_name = json.load(f)

object_to_family = {}
object_to_segment = {}
word_to_family = {}
word_to_segment = {}
for cluster in clusters:
    for word in clusters[cluster]:
        appearance_for_family_for_word = {}
        appearance_for_segment_for_word = {}
        for family, words in family_to_example.items():
            if word in words:
                if family not in appearance_for_family_for_word:
                    appearance_for_family_for_word[family] = 0
                for segment, families_in_segment in segment_name_to_family_name.items():
                    if family in families_in_segment:
                        if segment not in appearance_for_segment_for_word:
                            appearance_for_segment_for_word[segment] = 0
                        appearance_for_segment_for_word[segment]+=1
                appearance_for_family_for_word[family]+=1
        word_to_family[word] = appearance_for_family_for_word
        word_to_segment[word] = appearance_for_segment_for_word

# with open('word_to_family.json', 'w', encoding='utf-8') as f:
#     json.dump(word_to_family, f, ensure_ascii=False, indent=4)




for product in all_products:
    words_in_prod = product.split()
    for_product_family_count = {}
    for_product_segment_count = {}
    for word_in_prod in words_in_prod:
        if word_in_prod in word_to_family:
            for family in word_to_family[word_in_prod]:
                if family not in for_product_family_count:
                    for_product_family_count[family] = 0
                for_product_family_count[family]+=word_to_family[word_in_prod][family]
                for segment in word_to_segment[word_in_prod]:
                    if segment not in for_product_segment_count:
                        for_product_segment_count[segment] = 0
                    for_product_segment_count[segment]+=word_to_segment[word_in_prod][segment]
    # if for_product_segment_count!={}:
    object_to_segment[product] = for_product_segment_count
    object_to_family[product] = for_product_family_count
    
with open('family_to_code.json', 'r') as f:
    family_to_code = json.load(f)

# for every product in object_to_family print the inner dictionary entry with the bigggest value
with open('output_trial_2.txt', 'w') as file:
    file.write('')
with open('final.csv', 'w') as file:
    file.write('Product,Family\n')
with open('url_product_extraction_output_dataset.csv', 'r') as file:
    reader = csv.DictReader(file)
    for line in reader:
        url, product = line['url'], line['product_name']
        if product == "":
            product = "None"
        # print(f"url, {url}, product, .{product}.")
        
        if product == "None":
            with open('final.csv', 'a') as file_write_final:
                file_write_final.write(f"{url},,\n")
        
            # if product in object_to_family:
        elif product in object_to_family:
            max_value = -1
            family = ''
            for family in object_to_family[product]:
                if object_to_family[product][family] > max_value:
                    max_value = object_to_family[product][family]
                    family = family
            # print to csv file
            with open('final.csv', 'a') as file_write_final:
                try:
                    # print to file
                    file_write_final.write(f"{url},{product},{family_to_code[family]}\n")
                    # print(f"{product},{family_to_code[family]}")
                except KeyError:
                    file_write_final.write(f"{url},{product},Unknown\n")
                    # print(f"{product},unknown")
            # sort the object_to_segment[product] dictionary by value
            try:
                if object_to_segment[product]:
                    # Find the key with the maximum value in the dictionary
                    highest_family = max(object_to_segment[product], key=object_to_segment[product].get)
                    # print(f"{product} belongs to the {highest_family}  and family with a score of {object_to_segment[product][highest_family]}")
                else:
                    # If the dictionary is empty or product does not exist, write to the file
                    with open('output_trial_2.txt', 'a') as file:
                        file.write(product + '\n')
            except KeyError:
                print(f"Error: {product} is not a valid key.")
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")


            # this is good!!!
            # object_to_segment[product] = dict(sorted(object_to_segment[product].items(), key=lambda item: item[1], reverse=True))
            # print(f"{product} belongs to {object_to_segment[product]} family")
            # if object_to_segment[product] == {}:
            #     with open('output_trial_2.txt', 'a') as file:
            #         file.write(product + '\n')
        else:
            with open('final.csv', 'a') as file_write_final:
                file_write_final.write(f"{url},{product},Unknown\n")





























# print("\n\n\n\n\n\n\n\n\n\n\n------------------------------------------------------\n\n\n\n\n\n\n\n\n\n\n")


# # Initialize lists and dictionaries
# all_words = list(example_to_family.keys())  # Starting with predefined words
# word_list = [word for word in all_words if nlp.vocab.has_vector(word)]


# all_products = []
# # Read additional words from a text file
# count_word_vec = 0
# with open('output_trial_2.txt', 'r') as file:
#     for line in file:
#         all_products.append(line.strip())
#         for word in line.strip().split():
#             if word not in all_words:
#                 all_words.append(word)
#                 if nlp.vocab.has_vector(word):
#                     word_list.append(word)
#                     count_word_vec+=1
# print(count_word_vec)
                    

# # Prepare word vectors
# word_vectors = [nlp(word).vector for word in word_list]

# # Set number of clusters
# num_clusters = min(len(word_vectors), 100)

# # Perform K-means clustering
# if len(word_vectors) >= num_clusters and num_clusters > 0:
#     kmeans = KMeans(n_clusters=num_clusters, random_state=42)
#     kmeans.fit(word_vectors)
#     labels = kmeans.labels_

#     # Organizing words into clusters
#     clusters = {}
#     for i in range(num_clusters):
#         clusters[f"Cluster {i}"] = [word_list[j] for j in range(len(word_list)) if labels[j] == i]

#     # Save to JSON
#     with open('clusters.json', 'w', encoding='utf-8') as f:
#         json.dump(clusters, f, ensure_ascii=False, indent=4)

#     # Save to CSV
#     with open('clusters.csv', 'w', newline='', encoding='utf-8') as f:
#         writer = csv.writer(f)
#         writer.writerow(['Cluster Index', 'Words'])
#         for i in range(num_clusters):
#             words_in_cluster = ", ".join(clusters[f"Cluster {i}"])
#             writer.writerow([f"Cluster {i}", words_in_cluster])
# else:
#     print("Not enough word vectors to perform clustering or the number of clusters is set to zero.")

# clusters = {}
# with open('clusters.csv', 'r') as f:
#     reader = csv.reader(f)
    
#     for row in reader:
#         if row[0] != 'Cluster Index':
#             clusters[row[0]] = row[1].split(', ')

# # print(clusters)

# segment_name_to_family_name = {}
# with open('segment_name_to_family_name.json', 'r') as f:
#     segment_name_to_family_name = json.load(f)

# object_to_family = {}
# object_to_segment = {}
# word_to_family = {}
# word_to_segment = {}
# for cluster in clusters:
#     for word in clusters[cluster]:
#         appearance_for_family_for_word = {}
#         appearance_for_segment_for_word = {}
#         for family, words in family_to_example.items():
#             if word in words:
#                 if family not in appearance_for_family_for_word:
#                     appearance_for_family_for_word[family] = 0
#                 for segment, families_in_segment in segment_name_to_family_name.items():
#                     if family in families_in_segment:
#                         if segment not in appearance_for_segment_for_word:
#                             appearance_for_segment_for_word[segment] = 0
#                         appearance_for_segment_for_word[segment]+=1
#                 appearance_for_family_for_word[family]+=1
#         word_to_family[word] = appearance_for_family_for_word
#         word_to_segment[word] = appearance_for_segment_for_word

# # with open('word_to_family.json', 'w', encoding='utf-8') as f:
# #     json.dump(word_to_family, f, ensure_ascii=False, indent=4)




# for product in all_products:
#     words_in_prod = product.split()
#     for_product_family_count = {}
#     for_product_segment_count = {}
#     for word_in_prod in words_in_prod:
#         if word_in_prod in word_to_family:
#             for family in word_to_family[word_in_prod]:
#                 if family not in for_product_family_count:
#                     for_product_family_count[family] = 0
#                 for_product_family_count[family]+=word_to_family[word_in_prod][family]
#                 for segment in word_to_segment[word_in_prod]:
#                     if segment not in for_product_segment_count:
#                         for_product_segment_count[segment] = 0
#                     for_product_segment_count[segment]+=word_to_segment[word_in_prod][segment]
#     # if for_product_segment_count!={}:
#     object_to_segment[product] = for_product_segment_count
#     object_to_family[product] = for_product_family_count

# # for every product in object_to_family print the inner dictionary entry with the bigggest value
# for product in object_to_family:
#     max_value = -1
#     family = ''
#     for family in object_to_family[product]:
#         if object_to_family[product][family] > max_value:
#             max_value = object_to_family[product][family]
#             family = family
#     print(f"{product} belongs to {family} family")
#     print(f"{product} belongs to {object_to_segment[product]} family")