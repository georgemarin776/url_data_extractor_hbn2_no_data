from parse_urls import URL
import csv
from shopify_json import get_shopify_json
import enchant
from iso_country_codes import CC
import spacy
from spacy.training import Example
from sklearn.feature_extraction.text import CountVectorizer

from sklearn import svm
from sklearn import datasets

def read_csv(file_path):

    data = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            data.append(row)

    return data

def is_english_word(word):
    d = enchant.Dict("en_US")  # Load the English dictionary
    if not d.check(word):
        print(f"{word} is not an English word")
        print(d.suggest(word))
        return False
    return True

def split_path(path):
    components = path.split('/')
    for component in components:
        #replace - with space
        component = component.replace('-', ' ')
        #replace _ with space
        component = component.replace('_', ' ')
    return ' '.join(components)

if __name__ == "__main__":
    requests_buget = 100
    final_answers = {}
    data = read_csv('url_product_extraction_input_dataset.csv')

    found_products = 0

    downloaded_jsons = {}

    urls_with_products = []

    promising_urls = []

    # Define query parameters that indicate a single product page
    single_product_indicators = {'product_id', 'productId', 'pid', 'Itemid', 'product', 'sku', 'product-page'}

    # Define query parameters that indicate a page with multiple links
    multiple_links_indicators = {'category', 'tag', 'sort', 'orderby', 'page', 'per_page', 'filter', 'search', 'q', 'products-per-page'}

    bad_keywords = ["collections", "about-us", "contact", "faq", "policy", "terms", "about", "how", "product-category", "product-tag", "order", "list"]

    with open('bad_hrefs.txt', 'r') as file:
        bad_hrefs = file.read().splitlines()


    # read promising keywords
    with open('promising_keywords.txt', 'r') as file:
        promising_keywords = file.read().splitlines()

    alte_limbi = 0

    other_urls = []
    for row in data:
        final_answers[row['url']] = None
        url = URL(row['url'])
        if url.path == None or url.path == '':
            continue
        # if url.language != CC['EN'] and url.language != None:
        #     alte_limbi += 1
        #     final_answers[url.initial_url] = None
        #     continue
        if url.slash_products_path != None:
            urls_with_products.append(url)
            already_added = True
        else:
            already_added = False
            for kword in promising_keywords:
                if f"/{kword}/" in url.url:
                    url.slash_products_path = url.url[url.url.index(f"/{kword}/") + len(f"/{kword}/"):]
                    promising_urls.append(url)
                    already_added = True
                    break
            if already_added:
                final_answers[url.initial_url] = None
                continue

            for kword in bad_keywords:
                if kword in url.url.lower():
                    already_added = True
                    break
            if already_added:
                final_answers[url.initial_url] = None
                continue

            for key in url.query_params.keys():
                if key in multiple_links_indicators:
                    already_added = True
                    break
            if already_added:
                final_answers[url.initial_url] = None
                continue

            if row['href_text'] in bad_hrefs:
                final_answers[url.initial_url] = None
                continue

            other_urls.append(url)

    for url in urls_with_products:
        # filtru de query params
        is_not_product = False
        if url.query_params != {}:
            for key in url.query_params.keys():
                if key in single_product_indicators:
                    break
                if key in multiple_links_indicators:
                    is_not_product = True
                    break

        if is_not_product:
            continue

        maybe_product_name = ''
        sub_path = url.url[url.url.index('/products/') + len('/products/'):]
        if sub_path != '' and '/' not in sub_path:
            # remove .html if present
            maybe_product_name = sub_path.replace('.html', '')
            maybe_product_name = maybe_product_name.replace('.php', '')
            maybe_product_name = maybe_product_name.replace('.htm', '')

            #split at - or _ and keep only valid words or numbers
            if '-' in maybe_product_name:
                maybe_product_name = maybe_product_name.split('-')
            else:
                maybe_product_name = maybe_product_name.split('_')
            maybe_product_name = [word for word in maybe_product_name if word != '' and word.isalnum()]
            maybe_product_name = ' '.join(maybe_product_name)

            # aici apelam nlp-ul si vedem cat de mult crede ca e chiar un nume de produs
            # momentan doar printam
            if len(maybe_product_name) > 5:
                found_products += 1
                url.product_name = maybe_product_name


        if len(maybe_product_name) > 5:
            continue

        if requests_buget == 0:
            continue

        # construim url-ul din url-ul initial, inlocuind /products/ cu /products.json si stergand ce e dupa
        products_url =  url.url.replace('/products/', '/products.json')[0:url.url.index('/products/') + len('/products.json')]
        

        # cached jsons
        if products_url in downloaded_jsons:
            shopify_json = downloaded_jsons[products_url]
        else:
            shopify_json = get_shopify_json(products_url)
            requests_buget -= 1
            # print("\n\ntried to download" + products_url)
            # print(f"Requests left: {requests_buget}\n\n")
            downloaded_jsons[products_url] = shopify_json

        if shopify_json == None:
            continue
        
        if 'products' not in shopify_json:
            continue
        for product in shopify_json['products']:
            if 'pr_rec_pid' in url.query_params:
                if url.query_params['pr_rec_pid'][0] == product['id']:
                    maybe_product_name = product['title']
                    break
            variant_found = False
            if 'variant' in url.query_params:
                for variant in product['variants']:
                    if url.query_params['variant'][0] == variant['id']:
                        maybe_product_name = product['title']
                        variant_found = True
                        break
            if variant_found:
                break
            if product['handle'] in url.url:
                maybe_product_name = product['title']
                break
        
        url.product_name = maybe_product_name
        found_products += 1

    for url in promising_urls:
        # set maybe product name as the last part of the path

        is_not_product = False
        if url.query_params != {}:
            for key in url.query_params.keys():
                if key in single_product_indicators:
                    break
                if key in multiple_links_indicators:
                    is_not_product = True
                    break

        if is_not_product:
            continue

        maybe_product_name = url.slash_products_path.split('/')[0]
        # remove .html if present
        maybe_product_name = maybe_product_name.replace('.html', '')
        maybe_product_name = maybe_product_name.replace('.php', '')
        maybe_product_name = maybe_product_name.replace('.htm', '')
        #split at - or _ and keep only valid words or numbers
        if '-' in maybe_product_name:
            maybe_product_name = maybe_product_name.split('-')
        else:
            maybe_product_name = maybe_product_name.split('_')
        maybe_product_name = [word for word in maybe_product_name if word != '' and word.isalnum()]
        maybe_product_name = ' '.join(maybe_product_name)

        url.product_name = maybe_product_name
        found_products += 1

    for url in urls_with_products:
        if url.product_name != None:
            final_answers[url.initial_url] = url.product_name
        else:
            final_answers[url.initial_url] = None

    for url in promising_urls:
        if url.product_name != None:
            final_answers[url.initial_url] = url.product_name
        else:
            final_answers[url.initial_url] = None

    for url in other_urls:
        final_answers[url.initial_url] = None

    for url in other_urls:
        if not url.url.isascii():
            final_answers[url.initial_url] = None
            continue

        if url.query_params != {}:
            for key in url.query_params.keys():
                if key in single_product_indicators:
                    final_answers[url.initial_url] = url.query_params[key][0]
                    url.product_name = url.query_params[key][0]
                    break
                if key in multiple_links_indicators:
                    final_answers[url.initial_url] = None
                    break

    print(f"Found {found_products} products")

    with open('url_product_extraction_output_dataset.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['url', 'product_name'])
        for row in data:
            writer.writerow([row['url'], final_answers[row['url']]])

    # print values in other file
    with open('values.txt', 'w') as file:
        for val in final_answers.values():
            if val != None and val != "":
                file.write(f"{val}\n")