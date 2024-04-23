The process should be as follows:

(1) main.py + parse_urls.py
- parse list of csv files, regex + keywords
- ignore urls with href = about us, contact etc
- urls + relevant string data model -> k means clustering algorithm

(2) gpt_api_calls/main.py
- gpt queries to generate relevant 100 words with disjunct meaning for each
    category (label for the k means cluster) and data model creation

(3) k_means_and_word_2_vec.py
- actual k means clustering happening, label is the category
    that matches the most
- output:
    - url + significant string + category, if category found and
        significant string is not empty
    - url + significant string + 'Unknown', if category not found
        and significant string is not empty
    - url + 'None' + 'None', if string is empty (category won't even
        be evaluated)

Check the following files:
- (1) main.py + url_data_extractor.py
- (2) gpt_api_calls/main.py
- (3) k_means_and_word_2_vec.py

