import re

def count_four_digit_number_lines(file_path):
    # This regex matches exactly four-digit numbers that start with a comma and end at a newline
    pattern = re.compile(r',\d{4}\n')
    
    count = 0
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if pattern.search(line):
                count += 1

    return count


def count_word_occurrences(file_path, word, case_sensitive=True):
    count = 0
    with open(file_path, 'r', encoding='utf-8') as file:
        if case_sensitive:
            # Case-sensitive match
            for line in file:
                count += line.count(word)
        else:
            # Case-insensitive match
            word = word.lower()
            for line in file:
                count += line.lower().count(word)

    return count

# Example Usage
file_path = 'final.csv'  # Replace with your file path
number_of_lines = count_four_digit_number_lines(file_path)
print(f"The number of lines with exactly four-digit numbers is: {number_of_lines}")

number_of_lines_with_word = count_word_occurrences(file_path, 'Unknown', case_sensitive=False)
print(f"The number of lines with the word 'Unknown' is: {number_of_lines_with_word}")
