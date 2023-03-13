import itertools
from PyPDF2 import PdfWriter, PdfReader
import os
import shutil

# specify the directory names
INPUT_DIR = 'inputs'
OUTPUT_DIR = 'output'

# creating output folder if not exists
if (not os.path.exists(OUTPUT_DIR)):
    os.mkdir(OUTPUT_DIR)

# Specify the input PDF file path and the output directory path
pdf_path = None

# gettings the list of pdfs
pdfs = [pdf for pdf in os.listdir(INPUT_DIR + "/") if pdf.endswith(".pdf")]


for pdf in pdfs:
    pdf_path = os.path.join(INPUT_DIR, pdf)
    output_dir = ""
    pdf_name = pdf[:-4]

    # setting output directory for each type of pdf
    os.mkdir(f'{OUTPUT_DIR}/{pdf}')
    output_dir = os.path.join(OUTPUT_DIR, pdf) + "/"

    # Open the PDF file and get the number of pages
    pdf_file = open(pdf_path, 'rb')
    pdf_reader = PdfReader(pdf_file)
    num_pages = len(pdf_reader.pages)


    # putting the original file in the output folder
    shutil.copy(INPUT_DIR + "/" + f"{pdf}", f"{output_dir}original.pdf")

    # Generate all possible combinations of page numbers in sets of 1 and 2
    page_combinations = []
    for i in range(1, 3):
        combinations = list(itertools.combinations(range(num_pages), i))
        page_combinations.extend(combinations)
    
    # Generate 2 PDF files with 1 page each for an input PDF file with 2 pages
    if num_pages == 2:
        # Split into combinations of 1
        for i, page_num in enumerate(range(num_pages)):
            pdf_writer = PdfWriter()
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)
            output_filename = f"{output_dir}/{pdf_name}-set-of-1-variant{page_num+1}.pdf"
            with open(output_filename, 'wb') as output_file:
                pdf_writer.write(output_file)

    # Generate 3 PDF files with 1 page each for an input PDF file with 3 pages
    if num_pages == 3:
        # Split into combinations of 2 and 1
        page_ranges = itertools.combinations(range(num_pages), 2)
        for i, page_range in enumerate(page_ranges):
            pdf_writer = PdfWriter()
            for page_num in page_range:
                pdf_writer.add_page(pdf_reader.pages[page_num])
            output_filename = f"{output_dir}-set-of-2-variant-{page_num+1}.pdf"
            with open(output_filename, 'wb') as output_file:
                pdf_writer.write(output_file)
            # print(f"Saved {output_filename} to {output_dir}")

        # Split into combinations of 1
        for i, page_num in enumerate(range(num_pages)):
            pdf_writer = PdfWriter()
            pdf_writer.add_page(pdf_reader.pages[page_num])
            output_filename = f"{output_dir}-set-of-1-variant-{i+1}.pdf"
            with open(output_filename, 'wb') as output_file:
                pdf_writer.write(output_file)
            # print(f"Saved {output_filename} to {output_dir}")

    # Generate all possible combinations of sets of 3 pages for an input PDF file with 6 pages
    if num_pages == 6:
        for page_set in [3, 2, 1]:

            page_combinations = []
            for combination in itertools.combinations(range(num_pages), page_set):
                page_combinations.append(combination)

            for i, combination in enumerate(page_combinations):
                # Create a new PDF writer and output file name
                pdf_writer = PdfWriter()
                output_filename = f"{output_dir}-set-of-{page_set}-variant-{i+1}.pdf"
                for page_num in combination:
                    page = pdf_reader.pages[page_num]
                    pdf_writer.add_page(page)

                # Write the PDF file to disk
                with open(output_filename, 'wb') as output_file:
                    pdf_writer.write(output_file)

    # Close the input PDF file
    pdf_file.close()
