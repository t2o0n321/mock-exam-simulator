"""Script to parse a DumpsPanda PDF and output questions to a JSON or CSV file."""

import csv  # For writing CSV files
import json  # For writing JSON files
import os  # For handling file paths and directories
import re  # For regular expression pattern matching and text cleaning
import sys  # For command-line argument handling and exiting

import PyPDF2  # For reading and extracting text from PDF files

# Define regex patterns for cleaning unwanted text from the PDF
PAGE_REGEX = r"\d+/210"  # Matches page numbers like "16/210"
PANDA_URL_REGEX = r"www\.dumpspanda\.com"  # Matches the URL "www.dumpspanda.com"
QUESTION_ANSWER_REGEX = r"Questions\sand\sAnswers\sPDF"  # Matches the "Questions and Answers PDF" text


def parse_pdf_full_text(pdf_path):
    """Parse the full text of the PDF after cleaning unwanted patterns."""
    # Open the PDF file in binary read mode
    with open(pdf_path, "rb") as file:
        # Create a PDF reader object to process the file
        reader = PyPDF2.PdfReader(file)
        # Get the total number of pages in the PDF
        num_pages = len(reader.pages)

        # Initialize an empty string to store the full text of the PDF
        full_text = ""
        # Loop through each page in the PDF
        for page_num in range(num_pages):
            # Get the page object for the current page
            page = reader.pages[page_num]
            # Extract the text from the page and append it to full_text with a newline
            full_text += page.extract_text() + "\n"

    # Split the extracted text into individual lines for line-by-line cleaning
    lines = full_text.splitlines()
    # Initialize a list to store cleaned lines
    cleaned_lines = []
    # Process each line to remove unwanted patterns
    for line in lines:
        # Remove page numbers (e.g., "16/210") from the line
        cleaned_line = re.sub(PAGE_REGEX, "", line)
        # Remove the URL "www.dumpspanda.com" from the line
        cleaned_line = re.sub(PANDA_URL_REGEX, "", cleaned_line)
        # Remove the "Questions and Answers PDF" text from the line
        cleaned_line = re.sub(QUESTION_ANSWER_REGEX, "", cleaned_line)
        # Only add the line to cleaned_lines if it’s not empty after cleaning
        if cleaned_line.strip():
            cleaned_lines.append(cleaned_line)

    # Rejoin the cleaned lines with newlines to form the final cleaned text
    return "\n".join(cleaned_lines)


def parse_exam_questions(full_text):
    """Parse questions, options, answers, and explanations from the cleaned text."""
    # Define regex patterns for parsing different parts of a question block
    # Matches "Question: <number>" followed by its content until the next question or end of text
    question_pattern = r"Question: (\d+)\n(.*?)(?=\nQuestion: |\Z)"
    # Matches options (e.g., "A. text") until the next option, Answer, Explanation, or Question
    option_pattern = r"([A-Z])\.\s*(.*?)(?=\n[A-Z]\.|\nAnswer:|\nExplanation:|\nQuestion: |\Z)"
    # Matches "Answer: <letter>" followed by Explanation, next Question, or end of text
    answer_pattern = r"Answer: ([A-Z])(?=\nExplanation:|\nQuestion: |\Z)"
    # Matches "Explanation:\n" followed by its content until the next Question or end of text
    explanation_pattern = r"Explanation:\n(.*?)(?=\nQuestion: |\Z)"

    # Initialize a list to store parsed question data
    questions = []
    # Find all question blocks in the cleaned text using the question_pattern
    question_matches = re.finditer(question_pattern, full_text, re.DOTALL)

    # Iterate over each question block found in the text
    for q_match in question_matches:
        # Extract the question number (e.g., "39")
        question_number = q_match.group(1)
        # Extract the entire question block content
        question_block = q_match.group(2).strip()

        # Extract the question text by splitting on the first "A. " (start of options)
        question_text_split = re.split(r"\nA\.\s", question_block, maxsplit=1)
        # The question text is everything before "A. ", stripped of whitespace
        question_text = question_text_split[0].strip()

        # Extract options (e.g., "A. text") from the question block
        options_matches = re.finditer(option_pattern, question_block, re.DOTALL)
        # Create a dictionary mapping option letters (e.g., "A") to their text (e.g., "text")
        options = {opt.group(1): opt.group(2).strip() for opt in options_matches}

        # Extract the correct answer letter (e.g., "A") using the answer_pattern
        answer_match = re.search(answer_pattern, question_block, re.DOTALL)
        # Store the answer letter if found, otherwise set to None
        answer = answer_match.group(1) if answer_match else None

        # Extract the explanation text using the explanation_pattern
        explanation_match = re.search(explanation_pattern, question_block, re.DOTALL)
        # Store the explanation text if found, otherwise set to None
        explanation = explanation_match.group(1).strip() if explanation_match else None

        # Create a dictionary with the parsed question data
        question_data = {
            "question_number": int(question_number),  # Convert question number to integer
            "question_text": question_text,  # Store the question text
            "options": options,  # Store the options dictionary (e.g., {"A": "text", "B": "text"})
            "answer": answer,  # Store the correct answer letter (e.g., "A")
            "explanation": explanation  # Store the explanation text
        }
        # Append the question data to the questions list
        questions.append(question_data)

    # Return the list of parsed questions
    return questions


def save_to_json(data, output_path):
    """Save parsed questions data to a JSON file."""
    # Open the output file in write mode with UTF-8 encoding
    with open(output_path, "w", encoding="utf-8") as file:
        # Write the parsed questions data to the file as JSON with indentation
        # ensure_ascii=False allows non-ASCII characters (e.g., special characters) to be written correctly
        json.dump(data, file, indent=4, ensure_ascii=False)


def save_to_csv(data, output_path):
    """Save parsed questions data to a CSV file."""
    # Open the output file in write mode with UTF-8 encoding and no extra newlines
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        # Define the CSV column headers
        fieldnames = ["question", "options", "correct"]
        # Create a CSV writer object with quoting for all fields
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

        # Write the header row to the CSV
        writer.writeheader()
        # Iterate over each parsed question entry
        for entry in data:
            # Extract and clean the question text
            question = entry["question_text"].strip()
            # Replace any newlines in the question text with spaces to ensure a single-line question
            question = question.replace("\n", " ")

            # Get the options dictionary and sort the keys (e.g., ["A", "B", "C", ...])
            options_dict = entry["options"]
            sorted_keys = sorted(options_dict.keys())  # Ensures options are in alphabetical order
            # Create a list of option texts in sorted order
            options_list = [options_dict[k] for k in sorted_keys]

            # Get the correct answer letter (e.g., "A")
            correct_letter = entry.get("answer")
            # Create a mapping of option letters to 0-based indices (A=0, B=1, ..., Z=25)
            option_index_map = {chr(65 + i): i for i in range(26)}
            # Initialize the correct index as None
            correct_index = None
            # If the correct letter exists in the map, assign its index
            if correct_letter in option_index_map:
                correct_index = option_index_map[correct_letter]

            # Write the question data as a row in the CSV
            writer.writerow({
                "question": question,  # Write the question text (now without newlines)
                "options": json.dumps(options_list, ensure_ascii=False),  # Write options as a JSON-encoded list
                "correct": str(correct_index) if correct_index is not None else ""  # Write the correct index as a string, or "" if None
            })


def main():
    """Main function to orchestrate parsing and saving exam questions."""
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 4:
        # Print usage instructions and exit with an error code
        print("Usage: python3 parse_dumpspanda_pdf.py <path_to_dumps_pdf> <path_to_output_file> <json|csv>")
        sys.exit(1)

    # Get the absolute path of the input PDF file from command-line arguments
    dumps_panda_path = os.path.abspath(sys.argv[1])
    # Get the absolute path of the output file
    output_path = os.path.abspath(sys.argv[2])
    # Get the output format ("json" or "csv") and convert to lowercase
    output_format = sys.argv[3].lower()

    # Validate the output format
    if output_format not in ("json", "csv"):
        # Print an error message and exit if the format is invalid
        print("Error: Output format must be 'json' or 'csv'.")
        sys.exit(1)

    # Check if the input PDF file exists
    if not os.path.exists(dumps_panda_path):
        # Print an error message and exit if the file doesn’t exist
        print(f"Error: The file {dumps_panda_path} does not exist.")
        sys.exit(1)

    # Get the directory of the output file
    output_dir = os.path.dirname(output_path)
    # If the output directory exists and doesn’t exist, create it
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # Parse the full text from the PDF, cleaning unwanted patterns
        full_text = parse_pdf_full_text(dumps_panda_path)
        # Parse the questions, options, answers, and explanations from the cleaned text
        questions = parse_exam_questions(full_text)

        # Save the parsed questions based on the specified output format
        if output_format == "json":
            save_to_json(questions, output_path)
        else:
            save_to_csv(questions, output_path)

        # Print a success message with the number of questions parsed and the output file path
        print(f"Parsed {len(questions)} questions. Output written to {output_path}")
    except FileNotFoundError as error:
        # Handle file not found errors (e.g., if the PDF file cannot be accessed)
        print(f"Error: {error}")
        sys.exit(1)
    except PermissionError as error:
        # Handle permission errors (e.g., if the script lacks write permissions for the output file)
        print(f"Error: Permission denied when accessing {error.filename}. Check file permissions.")
        sys.exit(1)
    except Exception as error:
        # Handle any other unexpected errors during parsing or saving
        print(f"An unexpected error occurred: {error}")
        sys.exit(1)


if __name__ == "__main__":
    # Entry point of the script: run the main function if the script is executed directly
    main()
