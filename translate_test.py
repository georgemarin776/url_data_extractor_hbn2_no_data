from deep_translator import GoogleTranslator
import csv
import json
import spacy

# Load spaCy model and process searched_link
nlp = spacy.load("en_core_web_lg")
# searched_doc = nlp('''100mm womens pointed toe pumps wedding party red bottoms high heels stiletto shoes 30''')
searched_doc = nlp('''This delicious, unique, nutty flavour from black sesame seeds is what sets this brittle candy apart. With no added flavours, this all natural delight will quickly become a household favourite''')

most_similar_segments = []
with open('uniques_segment.txt', 'r') as f:
    segments = list(nlp.pipe(f.read().splitlines()))
    # compute the most similar 10 segments
    for segment in segments:
        score = segment.similarity(searched_doc)
        most_similar_segments.append((segment, score))
    for segment, score in sorted(most_similar_segments, key=lambda x: x[1], reverse=True)[:10]:
        print(f"Similarity between '{segment.text}' and searched link: {score}")