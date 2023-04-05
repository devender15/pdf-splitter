import itertools
import PyPDF2
from PyPDF2 import PdfWriter, PdfReader
import os
import shutil
from rich import print as rprint
from rich.tree import Tree

# specify the directory names
INPUT_DIR = 'inputs'
OUTPUT_DIR = 'output'

# main code

# creating output folder if not exists
if (not os.path.exists(OUTPUT_DIR)):
    os.mkdir(OUTPUT_DIR)
else:
    shutil.rmtree(OUTPUT_DIR)
    os.mkdir(OUTPUT_DIR)

# Specify the input PDF file path and the output directory path
pdf_path = None

# gettings the list of pdfs
pdfs = [pdf for pdf in os.listdir(INPUT_DIR + "/") if pdf.endswith(".pdf")]

# initializing the counter for the total number of PDFs generated in the output folder
PDF_COUNT = 0
FAILED_PDF_COUNT = 0

# Define the page sizes
page_sizes = {
    "A3": (1191, 842),
    "A4": (842, 595),
    "A5": (595, 421),
}

rprint("[bold red]Script started...[/bold red]")

for pdf in pdfs:
    pdf_path = os.path.join(INPUT_DIR, pdf)
    pdf_name = pdf.split(".")[0]
    output_dir = os.path.join(OUTPUT_DIR, pdf_name)

    tree = Tree(f"🔰 [bold green]{pdf_name}[/bold green]")

    rprint(f"[bold red]Processing {pdf_name}...[/bold red]")

    # setting output directory for each type of pdf
    os.mkdir(output_dir)

    # Open the PDF file and get the number of pages
    pdf_file = open(pdf_path, 'rb')
    pdf_reader = PdfReader(pdf_file)
    num_pages = len(pdf_reader.pages)

    # putting the original file in the output folder
    shutil.copy(INPUT_DIR + "/" + f"{pdf}",
                os.path.join(output_dir, "original.pdf"))
    tree.add(f"[sandy_brown]Original PDF ✅[/sandy_brown]")
    PDF_COUNT += 1

    # Generate all possible combinations of page numbers in sets of 1 and 2
    page_combinations = []
    for i in range(1, 3):
        combinations = list(itertools.combinations(range(num_pages), i))
        page_combinations.extend(combinations)

    # Generate 2 PDF files with 1 page each for an input PDF file with 2 pages
    if num_pages == 2:
        # Split into combinations of 1
        for i, page_num in enumerate(range(num_pages)):
            try:
                pdf_writer = PdfWriter()
                page = pdf_reader.pages[page_num]

                for size_name, size in page_sizes.items():
                    # Create a new page object with the correct size
                    new_page = PyPDF2.pdf.PageObject.createBlankPage(
                        size[0], size[1])
                    new_page.mergeScaledTranslatedPage(page, scaleToFit=True)
                    pdf_writer.add_page(new_page)
                    output_filename = f"{pdf_name}_set-1_variant-{i+1}_{size_name}.pdf"
                    output_path = os.path.join(output_dir, output_filename)
                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)
                    PDF_COUNT += 1
                    tree.add(f"Set of 1 variant - {page_num+1} ✅")

                # pdf_writer.add_page(page)
                # output_filename = f"{pdf_name}_set-1_variant-{i+1}.pdf"
                # output_path = os.path.join(output_dir, output_filename)
                # with open(output_path, 'wb') as output_file:
                #     pdf_writer.write(output_file)
                # PDF_COUNT += 1
                # tree.add(f"Set of 1 variant - {page_num+1} ✅")

            except:
                FAILED_PDF_COUNT += 1
                tree.add(f"Set of 1 variant - {page_num+1} ❌")

    # Generate 3 PDF files with 1 page each for an input PDF file with 3 pages
    if num_pages == 3:
        # Split into combinations of 2 and 1
        page_ranges = itertools.combinations(range(num_pages), 2)
        for i, page_range in enumerate(page_ranges):
            try:
                pdf_writer = PdfWriter()
                for page_num in page_range:
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                # output_filename = f"{output_dir}/set-of-2-variant-{i+1}.pdf"
                output_filename = f"_set-2_variant-{i+1}.pdf"
                output_path = os.path.join(output_dir, output_filename)

                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                PDF_COUNT += 1
                tree.add(f"Set of 2 variant - {i+1} ✅")
                # rprint(f"[green][{pdf_name}] Generated {output_filename}[/green]")

            except Exception as e:
                FAILED_PDF_COUNT += 1
                # rprint("[bold red]Error:[/bold red] ", e, f" - {pdf_name} (Set of 2 variant - {page_num+1}")
                tree.add(f"Set of 2 variant - {i+1} ❌")

        # Split into combinations of 1
        for i, page_num in enumerate(range(num_pages)):
            try:
                pdf_writer = PdfWriter()
                page = pdf_reader.pages[page_num]
                pdf_writer.add_page(page)
                # output_filename = f"{output_dir}/set-of-1-variant-{i+1}.pdf"
                output_filename = f"{pdf_name}_set-1_variant-{i+1}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
                PDF_COUNT += 1
                tree.add(f"Set of 1 variant - {page_num+1} ✅")

            except:
                FAILED_PDF_COUNT += 1
                tree.add(f"Set of 1 variant - {page_num+1} ❌")

    # Generate all possible combinations of sets of 3 pages for an input PDF file with 6 pages
    if num_pages == 6:
        for page_set in [3, 2, 1]:

            page_combinations = []
            for combination in itertools.combinations(range(num_pages), page_set):
                page_combinations.append(combination)

            for i, combination in enumerate(page_combinations):
                try:
                    # Create a new PDF writer and output file name
                    pdf_writer = PdfWriter()
                    # output_filename = f"{output_dir}/set-of-{page_set}-variant-{i+1}.pdf"
                    output_filename = f"{pdf_name}_set-{page_set}_variant-{i+1}.pdf"
                    output_path = os.path.join(output_dir, output_filename)

                    for page_num in combination:
                        page = pdf_reader.pages[page_num]
                        pdf_writer.add_page(page)

                    # Write the PDF file to disk
                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)

                    PDF_COUNT += 1
                    tree.add(f"Set of {page_set} variant - {i+1} ✅")

                except:
                    FAILED_PDF_COUNT += 1
                    tree.add(f"Set of {page_set} variant - {i+1} ❌")

    # showing the tree
    rprint(tree)

    # Close the input PDF file
    pdf_file.close()

# showing the summary of the output
rprint(
    "-------------------------[bold red]Summary of the output-------------------------")
rprint(f"[dark_olive_green2]Input directory: {INPUT_DIR}[/dark_olive_green2]")
rprint(
    f"[dark_olive_green2]Output directory: {OUTPUT_DIR}[/dark_olive_green2]")
rprint(f"[dark_olive_green2]Total input PDFs: {len(pdfs)}[/dark_olive_green2]")
rprint(
    f"[dark_olive_green2]Total PDFs in output: {len(os.listdir(OUTPUT_DIR))}[/dark_olive_green2]")
rprint(
    f"[dark_olive_green2]Total PDFs generated: {PDF_COUNT}[/dark_olive_green2]")
rprint(
    f"[dark_olive_green2]Total PDFs failed: {FAILED_PDF_COUNT}[/dark_olive_green2]")
