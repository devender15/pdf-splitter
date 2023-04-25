import itertools
import PyPDF2
from PyPDF2 import PdfWriter, PdfReader
import os
import shutil
from rich import print as rprint
from rich.tree import Tree
import fitz
from PIL import Image


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
PAGE_SIZES = {
    "A3": {
        "width": 842,
        "height": 1191,
    },
    "A4": {
        "width": 595,
        "height": 842,
    },
    "A5": {
        "width": 420,
        "height": 595,
    },
}

# functions

def generateImages(pdf_name, output_folder):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    doc = fitz.open(pdf_name)

    for i, page in enumerate(doc):
        image_name = f"page_{i+1}.jpg"
        image_path = os.path.join(output_folder, image_name)
        pix = page.get_pixmap()
        pix._writeIMG(image_path, format=100)

        # Open the image file with PIL
        image = Image.open(image_path)

        # Resize the image to A3 size (297 x 420 mm)
        a3_size = (PAGE_SIZES["A3"]['width'], PAGE_SIZES["A3"]['height'])
        image_a3 = image.resize(a3_size)
        image_a3.save(os.path.join(output_folder, f"a3_{image_name}"))

        # Resize the image to A4 size (210 x 297 mm)
        a4_size = (PAGE_SIZES["A4"]['width'], PAGE_SIZES["A4"]['height'])
        image_a4 = image.resize(a4_size)
        image_a4.save(os.path.join(output_folder, f"a4_{image_name}"))

        # Resize the image to A5 size (148 x 210 mm)
        a5_size = (PAGE_SIZES["A5"]['width'], PAGE_SIZES["A5"]['height'])
        image_a5 = image.resize(a5_size)
        image_a5.save(os.path.join(output_folder, f"a5_{image_name}"))

        # delete the original image
        os.remove(image_path)


def savePDF(output_dir, output_filename):
    # creating a folder of this variant
    os.mkdir(os.path.join(
        output_dir, output_filename.split(".")[0]))

    # saving this variant in this new folder
    with open(os.path.join(output_dir, output_filename.split(".")[0], output_filename), 'wb') as output_file:
        pdf_writer.write(output_file)

    # create a folder named 'jpeg' inside this new folder
    os.mkdir(os.path.join(
        output_dir, output_filename.split(".")[0], "jpg"))
    os.mkdir(os.path.join(
        output_dir, output_filename.split(".")[0], "pdfs"))

    tree.add(f"---> Generating images for {output_filename}...")

    # generate images from this pdf
    generateImages(os.path.join(output_dir, output_filename.split(".")[0], output_filename),
                   os.path.join(output_dir, output_filename.split(".")[0], "jpg"))

    # create a .zip file of the parent folder and delete the parent folder
    tree.add(f"---> Creating a .zip file for {output_filename}...")

    shutil.make_archive(os.path.join(output_dir, output_filename.split(
        ".")[0]), 'zip', os.path.join(output_dir, output_filename.split(".")[0]))

    shutil.rmtree(os.path.join(
        output_dir, output_filename.split(".")[0]))


rprint("[bold violet]Script started...[/bold violet]")

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
                pdf_writer.add_page(page)
                output_filename = f"{pdf_name}_set-1_variant-{i+1}.pdf"
                savePDF(output_dir, output_filename)

                PDF_COUNT += 1
                tree.add(f"Set of 1 variant - {page_num+1} ✅")

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
                output_filename = f"{pdf_name}_set-2_variant-{i+1}.pdf"
                savePDF(output_dir, output_filename)

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
                output_filename = f"{pdf_name}_set-1_variant-{i+1}.pdf"
                savePDF(output_dir, output_filename)

                PDF_COUNT += 1
                tree.add(f"Set of 1 variant - {page_num+1} ✅")

            except Exception as e:
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

                    for page_num in combination:
                        page = pdf_reader.pages[page_num]
                        pdf_writer.add_page(page)
                        output_filename = f"{pdf_name}_set-{page_set}_variant-{i+1}.pdf"
                        savePDF(output_dir, output_filename)

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
