import csv
from urllib.parse import urlparse, parse_qs
from collections import defaultdict

def extract_query_statistics(input_csv_path, output_csv_path):
    # Dictionary to store frequency of each query parameter
    query_counts = defaultdict(int)
    
    # Open the CSV file and read urls from it
    with open(input_csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row:  # Check if row is not empty
                url = row[0]
                parsed_url = urlparse(url)
                if not "produkt" in parsed_url.path:
                    print(f"Skipping {url} as it is a pagination URL")
                    continue
                queries = parse_qs(parsed_url.query)
                for param in queries:
                    query_counts[param] += 1

    # Open a new CSV file to write the statistics
    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Query Parameter', 'Frequency'])  # Write header
        sorted_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Write each query parameter and its frequency to the CSV file
        for query, count in sorted_queries:
            writer.writerow([query, count])

# Example usage: adjust 'input_file.csv' and 'output_file.csv' to your file paths
extract_query_statistics('url_product_extraction_input_dataset.csv', 'abaoutput_file.csv')
