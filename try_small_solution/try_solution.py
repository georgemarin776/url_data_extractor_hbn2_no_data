import spacy
import json
import time
import csv
import re
from urllib.parse import urlparse, parse_qs

nlp = spacy.load("en_core_web_lg")

def load_unique_segments(filepath):
    unique_segments = set()
    with open(filepath, 'r') as file:
        for line in file:
            unique_segments.add(line.strip())
    return unique_segments


def return_csv_data(filepath):
    data = []
    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data


english_domains = { 'us', 'uk', 'ca', 'au', 'nz', 'ie', 'com', 'net', 'org', 'edu', 'gov', 'mil', 'int', 'arpa', 'online', 'co'}
def is_english_speaking_domain(url):
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        top_level_domain = domain.split('.')[-1]
        return top_level_domain in english_domains
    except:
        return False


def get_text_from_url(url):
    try:
        parsed_url = urlparse(url)
        domain_parts = parsed_url.netloc.split('.')
        if len(domain_parts) > 2 and domain_parts[-2] in ('co', 'com', 'org', 'net'):
            domain_text = ' '.join(domain_parts[:-2])
        else:
            domain_text = ' '.join(domain_parts[:-1]) 
        domain_text = re.sub(r'\W+', ' ', domain_text).strip()
        
        path_segments = [re.sub(r'\W+', ' ', segment).strip() for segment in parsed_url.path.split('/') if segment]
        path_text = ' '.join(path_segments)
        
        query_params = parse_qs(parsed_url.query)
        query_text_parts = []
        for param, values in query_params.items():
            for value in values:
                cleaned_value = re.sub(r'\W+', ' ', value).strip()
                query_text_parts.append(cleaned_value)
        query_text = ' '.join(query_text_parts)
        
        full_text = ' '.join([domain_text, path_text, query_text]).strip()
        return full_text
    except:
        return ''


def get_text_from_href(href):
    try:
        href_text = re.sub(r'\W+', ' ', href).strip()
        return href_text
    except:
        return ''


def get_english_urls(target_data):
    for data in target_data:
        url = data['url']
        if is_english_speaking_domain(url):
            yield data


def get_text_from_english_url(english_url):
    url = english_url['url']
    href = english_url['href_text']
    text = get_text_from_url(url)
    if not href:
        text += ' ' + get_text_from_href(href)
    return text


def load_segment_to_family(filepath):
    with open(filepath, 'r') as file:
        segment_to_family = json.load(file)
    return segment_to_family


def load_family_to_commodity(filepath):
    with open(filepath, 'r') as file:
        family_to_commodity = json.load(file)
    return family_to_commodity


# def npl_match()



if __name__ == '__main__':
    initial_time = time.time()

    target_data_csv = 'small_dataset.csv'
    segment_to_family_filepath = 'segment_to_family.json'
    family_to_commodity_filepath = 'family_to_commodity.json'
    unique_segments_filepath = 'unique_segments.txt'

    target_data = return_csv_data(target_data_csv)
    segment_to_family = load_segment_to_family(segment_to_family_filepath)
    family_to_commodity = load_family_to_commodity(family_to_commodity_filepath)
    unique_segments = load_unique_segments(unique_segments_filepath)


    result_mapping = {}
    input_order = []
    for data in target_data:
        input_order.append(data['url'])
        result_mapping[data['url']] = None

    english_urls = list(get_english_urls(target_data))
    for english_url in english_urls:
        text = get_text_from_english_url(english_url)
        
        max_similarity = -1
        max_segment = None

        for segment in unique_segments:
            segment_doc = nlp(segment)
            text_doc = nlp(text)
            similarity = segment_doc.similarity(text_doc)
            if similarity > max_similarity:
                max_similarity = similarity
                max_segment = segment
        
        max_similarity = -1
        max_family = None
        for family in segment_to_family[max_segment]:
            family_doc = nlp(family)
            similarity = family_doc.similarity(text_doc)
            if similarity > max_similarity:
                max_similarity = similarity
                max_family = family
            
        result_mapping[english_url['url']] = max_family

    with open('result.json', 'w') as file:
        json.dump(result_mapping, file)

    print('Time taken:', time.time() - initial_time)