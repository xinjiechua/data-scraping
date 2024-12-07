import os
import csv

# Path to the directory containing the PDF files
pdf_directory = 'Federal Legislation/subsidiary_pu_a'

# Output CSV file path
csv_file_path = 'pu_a_saved_filename.csv'

# Get a list of all PDF files in the directory
pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]

# Write the file names to a CSV file
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['PDF File Name'])  # Write the header
    for pdf_file in pdf_files:
        writer.writerow([pdf_file])  # Write each PDF file name

print(f"PDF file names have been saved to {csv_file_path}")
