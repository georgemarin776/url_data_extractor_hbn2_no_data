import csv
from collections import Counter

def analyze_href_text(input_csv_path, output_csv_path):
    # This function reads a CSV file, counts occurrences of href texts, and writes the results to another CSV file.

    # Read href texts from the input CSV file
    href_texts = []
    with open(input_csv_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)  # Using DictReader to easily access columns by name
        for row in reader:
            href_texts.append((row['href_text']).lower())  # Append the text associated with the href

    # Count the frequency of each unique href text
    href_text_counts = Counter(href_texts)

    # Write the counts to the output CSV file
    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Href Text', 'Count'])  # Write the header row
        # sort the href text by count
        href_text_counts = dict(sorted(href_text_counts.items(), key=lambda item: item[1], reverse=True))
        for href_text, count in href_text_counts.items():
            # write making it lower case
            writer.writerow([href_text, count])

# Example usage
analyze_href_text('rows_with_not_null_href.csv', 'href_text_statistics.csv')
