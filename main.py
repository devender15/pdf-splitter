import itertools
from PyPDF2 import PdfWriter, PdfReader
import os


# creating output folder if not exists
if (not os.path.exists('output')):
    os.mkdir('output')

# Specify the input PDF file path and the output directory path
pdf_path = None

# gettings the list of pdfs
pdfs = [pdf for pdf in os.listdir("inputs/") if pdf.endswith(".pdf")]

for pdf in pdfs:
    pdf_path = os.path.join("inputs", pdf)
    output_dir = ""

    # setting output directory for each type of pdf
    os.mkdir(f'output/{pdf}')
    output_dir = os.path.join("output/", pdf) + "/"

    # Open the PDF file and get the number of pages
    pdf_file = open(pdf_path, 'rb')
    pdf_reader = PdfReader(pdf_file)
    num_pages = len(pdf_reader.pages)

    # putting the original file in the output folder
    with open(f"{output_dir}original.pdf", 'wb') as output_file:
        output_file.write(pdf_file.read())

    # Generate all possible combinations of page numbers in sets of 1 and 2
    page_combinations = []
    for i in range(1, 3):
        combinations = list(itertools.combinations(range(num_pages), i))
        page_combinations.extend(combinations)

    # Iterate through each combination of page numbers and create a new PDF file
    for i, combination in enumerate(page_combinations):
        # Create a new PDF writer and output file name
        pdf_writer = PdfWriter()
        output_filename = f"{output_dir}-{i+1}-"
        for j, page_num in enumerate(combination):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)
            output_filename += str(page_num+1)
            if j < len(combination)-1:
                output_filename += "-"
        output_filename += ".pdf"

        # Write the PDF file to disk
        with open(output_filename, 'wb') as output_file:
            pdf_writer.write(output_file)

    # Generate 3 PDF files with 1 page each for an input PDF file with 3 pages
    if num_pages == 3:
        for page_num in range(num_pages):
            pdf_writer = PdfWriter()
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)
            output_filename = f"{output_dir}-single-page-{page_num+1}.pdf"
            with open(output_filename, 'wb') as output_file:
                pdf_writer.write(output_file)

    # Generate all possible combinations of sets of 3 pages for an input PDF file with 6 pages
    if num_pages == 6:
        page_combinations = []
        for combination in itertools.combinations(range(num_pages), 3):
            page_combinations.append(combination)

        for i, combination in enumerate(page_combinations):
            # Create a new PDF writer and output file name
            pdf_writer = PdfWriter()
            output_filename = f"{output_dir}-set-of-3-pages-{i+1}.pdf"
            for page_num in combination:
                page = pdf_reader.pages[page_num]
                pdf_writer.add_page(page)

            # Write the PDF file to disk
            with open(output_filename, 'wb') as output_file:
                pdf_writer.write(output_file)

    # Close the input PDF file
    pdf_file.close()
